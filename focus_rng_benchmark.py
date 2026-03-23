"""
Focused RNG benchmark runner.

Compares CPU (sequential pseudo-RNG), GPU (parallel pseudo-RNG), and QPU (quantum RNG)
across workload sizes, then exports a unified report with:
- raw JSON
- flattened CSV
- summary JSON
- markdown report
- plots (execution time and resource footprint)
"""

import argparse
import csv
import json
import math
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from algorithms.rng_algorithm import RNGAlgorithm
from utils.helpers import set_seed

try:
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover - optional plotting dependency
    plt = None


PLATFORMS = ["CPU", "GPU", "QPU"]


def parse_counts(raw: str) -> List[int]:
    values = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        value = int(token)
        if value <= 0:
            raise ValueError(f"Count must be > 0. Found: {value}")
        values.append(value)
    if not values:
        raise ValueError("At least one count value is required.")
    return values


def resolve_qubits(
    count: int,
    mode: str,
    fixed_qubits: int,
    min_qubits: int,
    max_qubits: int,
) -> int:
    if mode == "fixed":
        return fixed_qubits

    # Logarithmic qubit growth in terms of workload size.
    # Capped to keep simulator runtime practical.
    recommended = int(math.ceil(math.log2(max(2, count))))
    return max(min_qubits, min(max_qubits, recommended))


def extract_row(
    run_idx: int,
    count: int,
    planned_qubits: int,
    platform: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    success = bool(data.get("success", False))
    time_s = float(data.get("generation_time", 0.0) or 0.0)
    throughput = float(data.get("numbers_per_second", 0.0) or 0.0)

    memory_mb = data.get("peak_memory_mb")
    if memory_mb is None:
        memory_mb = data.get("memory_used_mb")
    memory_mb = float(memory_mb) if memory_mb is not None else None

    qpu_qubits = None
    if platform == "QPU":
        qpu_qubits = data.get("num_qubits", planned_qubits)
        qpu_qubits = int(qpu_qubits) if qpu_qubits is not None else planned_qubits

    return {
        "run_index": run_idx,
        "count": count,
        "planned_qubits": planned_qubits,
        "platform": platform,
        "platform_runtime_label": data.get("platform", platform),
        "algorithm": data.get("algorithm", "Unknown"),
        "success": success,
        "error": data.get("error", ""),
        "execution_time_s": time_s,
        "throughput_numbers_per_s": throughput,
        "peak_memory_mb": memory_mb,
        "qpu_qubits": qpu_qubits,
        "time_per_item_s": (time_s / count) if time_s > 0 else None,
    }


def platform_rows(rows: List[Dict[str, Any]], platform: str) -> List[Dict[str, Any]]:
    return [r for r in rows if r["platform"] == platform]


def successful_rows(rows: List[Dict[str, Any]], platform: str) -> List[Dict[str, Any]]:
    return [r for r in platform_rows(rows, platform) if r["success"] and r["execution_time_s"] > 0]


def median_or_none(values: List[float]) -> Optional[float]:
    return statistics.median(values) if values else None


def mean_or_none(values: List[float]) -> Optional[float]:
    return statistics.mean(values) if values else None


def scaling_exponent(success_rows: List[Dict[str, Any]]) -> Optional[float]:
    points = [(r["count"], r["execution_time_s"]) for r in success_rows if r["execution_time_s"] > 0]
    if len(points) < 2:
        return None

    # Use one point per count for stability.
    by_count: Dict[int, float] = {}
    for count, timing in points:
        by_count[count] = timing
    if len(by_count) < 2:
        return None

    x = np.log(np.array(list(by_count.keys()), dtype=float))
    y = np.log(np.array(list(by_count.values()), dtype=float))
    slope, _intercept = np.polyfit(x, y, 1)
    return float(slope)


def build_summary(rows: List[Dict[str, Any]], counts: List[int]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "platforms": {},
        "speedups_vs_cpu": {},
        "qpu_qubit_scaling": {},
    }

    for platform in PLATFORMS:
        success = successful_rows(rows, platform)
        all_rows = platform_rows(rows, platform)
        times = [r["execution_time_s"] for r in success]
        throughputs = [r["throughput_numbers_per_s"] for r in success]
        memories = [r["peak_memory_mb"] for r in success if r["peak_memory_mb"] is not None]
        failures = [r for r in all_rows if not r["success"]]

        summary["platforms"][platform] = {
            "runs_total": len(all_rows),
            "runs_success": len(success),
            "runs_failed": len(failures),
            "mean_time_s": mean_or_none(times),
            "median_time_s": median_or_none(times),
            "mean_throughput_numbers_per_s": mean_or_none(throughputs),
            "best_throughput_numbers_per_s": max(throughputs) if throughputs else None,
            "mean_peak_memory_mb": mean_or_none(memories),
            "empirical_time_exponent": scaling_exponent(success),
            "notes": sorted({r["platform_runtime_label"] for r in all_rows}),
        }

    # Per-count speedups relative to CPU.
    for count in counts:
        summary["speedups_vs_cpu"][str(count)] = {}
        cpu = next(
            (
                r
                for r in rows
                if r["count"] == count and r["platform"] == "CPU" and r["success"] and r["execution_time_s"] > 0
            ),
            None,
        )
        if cpu is None:
            continue

        for platform in ["GPU", "QPU"]:
            other = next(
                (
                    r
                    for r in rows
                    if r["count"] == count
                    and r["platform"] == platform
                    and r["success"]
                    and r["execution_time_s"] > 0
                ),
                None,
            )
            if other is None:
                continue
            summary["speedups_vs_cpu"][str(count)][platform] = cpu["execution_time_s"] / other["execution_time_s"]

    qpu_success = successful_rows(rows, "QPU")
    if qpu_success:
        q_values = [r["qpu_qubits"] for r in qpu_success if r["qpu_qubits"] is not None]
        log2_counts = [math.log2(r["count"]) for r in qpu_success]
        ratios = [q / l for q, l in zip(q_values, log2_counts) if l > 0]

        summary["qpu_qubit_scaling"] = {
            "mean_qubits": mean_or_none([float(q) for q in q_values]),
            "mean_log2_count": mean_or_none(log2_counts),
            "mean_qubits_to_log2_count_ratio": mean_or_none(ratios),
        }

    return summary


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    fieldnames = [
        "run_index",
        "count",
        "planned_qubits",
        "platform",
        "platform_runtime_label",
        "algorithm",
        "success",
        "error",
        "execution_time_s",
        "throughput_numbers_per_s",
        "peak_memory_mb",
        "qpu_qubits",
        "time_per_item_s",
    ]

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _series(rows: List[Dict[str, Any]], platform: str, metric: str) -> (List[int], List[float]):
    subset = [r for r in rows if r["platform"] == platform and r["success"]]
    subset.sort(key=lambda r: r["count"])
    x: List[int] = []
    y: List[float] = []
    for r in subset:
        value = r.get(metric)
        if value is None:
            continue
        if isinstance(value, (int, float)):
            x.append(int(r["count"]))
            y.append(float(value))
    return x, y


def plot_execution_time(rows: List[Dict[str, Any]], out_path: Path) -> None:
    if plt is None:
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    for platform in PLATFORMS:
        x, y = _series(rows, platform, "execution_time_s")
        if x:
            ax.plot(x, y, marker="o", linewidth=2, label=platform)
    ax.set_title("Focus RNG: Execution Time vs Workload Size")
    ax.set_xlabel("Count (N)")
    ax.set_ylabel("Execution Time (s)")
    ax.set_xscale("log")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_resource_efficiency(rows: List[Dict[str, Any]], out_path: Path) -> None:
    if plt is None:
        return

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # CPU/GPU memory on left axis.
    for platform in ["CPU", "GPU"]:
        x, y = _series(rows, platform, "peak_memory_mb")
        if x:
            ax1.plot(x, y, marker="o", linewidth=2, label=f"{platform} Memory (MB)")

    ax1.set_xlabel("Count (N)")
    ax1.set_ylabel("Peak Memory (MB)")
    ax1.set_xscale("log")
    ax1.grid(True, alpha=0.3)

    # QPU qubits on right axis.
    ax2 = ax1.twinx()
    xq, yq = _series(rows, "QPU", "qpu_qubits")
    if xq:
        ax2.plot(xq, yq, marker="s", linewidth=2, color="tab:purple", label="QPU Qubits")
    ax2.set_ylabel("Qubit Count")

    # Merge legends.
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    if lines1 or lines2:
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    fig.suptitle("Focus RNG: Resource Usage (MB vs Qubit Count)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def write_markdown_report(
    path: Path,
    counts: List[int],
    qubit_mode: str,
    shots: int,
    rows: List[Dict[str, Any]],
    summary: Dict[str, Any],
) -> None:
    lines: List[str] = []
    lines.append("# Focus RNG Architecture Comparison Report")
    lines.append("")
    lines.append(f"- Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- Counts: {counts}")
    lines.append(f"- Qubit mode: `{qubit_mode}`")
    lines.append(f"- Shots: {shots}")
    lines.append("")
    lines.append("## Problem Framing")
    lines.append(
        "Performance and resource efficiency comparison of Focus Algorithm RNG across CPU (O(N)), "
        "GPU (O(N/P)), and QPU with logarithmic qubit representation."
    )
    lines.append("")
    lines.append("## Platform Summary")
    lines.append("")
    lines.append("| Platform | Success/Total | Mean Time (s) | Mean Throughput (/s) | Mean Peak Memory (MB) | Empirical Time Exponent |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for platform in PLATFORMS:
        item = summary["platforms"].get(platform, {})
        lines.append(
            f"| {platform} | {item.get('runs_success', 0)}/{item.get('runs_total', 0)} | "
            f"{_fmt(item.get('mean_time_s'))} | {_fmt(item.get('mean_throughput_numbers_per_s'))} | "
            f"{_fmt(item.get('mean_peak_memory_mb'))} | {_fmt(item.get('empirical_time_exponent'))} |"
        )
    lines.append("")

    lines.append("## Speedup vs CPU")
    lines.append("")
    lines.append("| Count (N) | GPU Speedup | QPU Speedup |")
    lines.append("| --- | --- | --- |")
    for count in counts:
        speedups = summary["speedups_vs_cpu"].get(str(count), {})
        lines.append(
            f"| {count} | {_fmt(speedups.get('GPU'))} | {_fmt(speedups.get('QPU'))} |"
        )
    lines.append("")

    lines.append("## QPU Scaling Check")
    lines.append("")
    qsc = summary.get("qpu_qubit_scaling", {})
    if qsc:
        lines.append(f"- Mean qubits: {_fmt(qsc.get('mean_qubits'))}")
        lines.append(f"- Mean log2(N): {_fmt(qsc.get('mean_log2_count'))}")
        lines.append(f"- Mean ratio qubits/log2(N): {_fmt(qsc.get('mean_qubits_to_log2_count_ratio'))}")
    else:
        lines.append("- No successful QPU runs to analyze.")
    lines.append("")

    failed = [r for r in rows if not r["success"]]
    if failed:
        lines.append("## Failures")
        lines.append("")
        lines.append("| Count | Platform | Error |")
        lines.append("| --- | --- | --- |")
        for row in failed:
            error = str(row.get("error", "")).replace("|", "/")
            lines.append(f"| {row['count']} | {row['platform']} | {error} |")
        lines.append("")

    lines.append("## Artifacts")
    lines.append("")
    lines.append("- `raw_runs.json`")
    lines.append("- `results.csv`")
    lines.append("- `summary.json`")
    lines.append("- `report.md`")
    lines.append("- `execution_time_vs_count.png`")
    lines.append("- `resource_efficiency.png`")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def _fmt(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.6g}"
    return str(value)


def run(args: argparse.Namespace) -> int:
    counts = parse_counts(args.counts)
    out_dir = Path(args.output_dir) if args.output_dir else (
        Path("results") / "reports" / f"focus_rng_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("Focus RNG Benchmark")
    print("=" * 80)
    print(f"Counts: {counts}")
    print(f"Qubit mode: {args.qubit_mode}")
    print(f"Output: {out_dir}")
    print("=" * 80)

    set_seed(args.seed)

    rows: List[Dict[str, Any]] = []
    raw_results: List[Dict[str, Any]] = []

    for idx, count in enumerate(counts, start=1):
        qubits = resolve_qubits(
            count=count,
            mode=args.qubit_mode,
            fixed_qubits=args.fixed_qubits,
            min_qubits=args.min_qubits,
            max_qubits=args.max_qubits,
        )
        print(f"\n[{idx}/{len(counts)}] Running count={count}, qubits={qubits}")

        algo = RNGAlgorithm(count=count, num_qubits=qubits, seed=args.seed)
        result = algo.run_comparison(platforms=PLATFORMS, shots=args.shots)
        raw_results.append(
            {
                "count": count,
                "num_qubits": qubits,
                "result": result,
            }
        )

        for platform in PLATFORMS:
            data = result.get("platforms", {}).get(platform, {})
            row = extract_row(
                run_idx=idx,
                count=count,
                planned_qubits=qubits,
                platform=platform,
                data=data,
            )
            rows.append(row)
            if row["success"]:
                print(
                    f"  [OK] {platform}: time={row['execution_time_s']:.6f}s "
                    f"rate={row['throughput_numbers_per_s']:.2f}/s"
                )
            else:
                print(f"  [FAIL] {platform}: {row['error']}")

    summary = build_summary(rows, counts)

    (out_dir / "raw_runs.json").write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "config": {
                    "counts": counts,
                    "qubit_mode": args.qubit_mode,
                    "fixed_qubits": args.fixed_qubits,
                    "min_qubits": args.min_qubits,
                    "max_qubits": args.max_qubits,
                    "shots": args.shots,
                    "seed": args.seed,
                },
                "runs": raw_results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    write_csv(out_dir / "results.csv", rows)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown_report(
        path=out_dir / "report.md",
        counts=counts,
        qubit_mode=args.qubit_mode,
        shots=args.shots,
        rows=rows,
        summary=summary,
    )

    if args.no_plots:
        print("\nSkipping plots (--no-plots set).")
    elif plt is None:
        print("\nSkipping plots (matplotlib is not installed).")
    else:
        plot_execution_time(rows, out_dir / "execution_time_vs_count.png")
        plot_resource_efficiency(rows, out_dir / "resource_efficiency.png")

    print("\nCompleted.")
    print(f"Artifacts written to: {out_dir}")
    print(f"Summary JSON: {out_dir / 'summary.json'}")
    print(f"Report: {out_dir / 'report.md'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Focused RNG benchmark across CPU/GPU/QPU with report export."
    )
    parser.add_argument(
        "--counts",
        type=str,
        default="100,1000,5000,10000",
        help="Comma-separated RNG sample counts (N).",
    )
    parser.add_argument(
        "--qubit-mode",
        choices=["fixed", "logn"],
        default="logn",
        help="How QPU qubits are selected per count.",
    )
    parser.add_argument("--fixed-qubits", type=int, default=5, help="Qubits when --qubit-mode=fixed.")
    parser.add_argument("--min-qubits", type=int, default=2, help="Minimum qubits in logn mode.")
    parser.add_argument("--max-qubits", type=int, default=10, help="Maximum qubits in logn mode.")
    parser.add_argument("--shots", type=int, default=1024, help="Quantum measurement shots.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="",
        help="Output directory. Default: results/reports/focus_rng_<timestamp>",
    )
    parser.add_argument("--no-plots", action="store_true", help="Skip plot generation.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
