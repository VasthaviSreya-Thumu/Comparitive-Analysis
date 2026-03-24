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
    trial_idx: int,
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
    backend_type = str(data.get("backend_type", "unknown"))
    backend_name = str(data.get("backend_name", "")) if data.get("backend_name") is not None else ""
    is_fallback = bool(data.get("is_fallback", False))

    return {
        "run_index": run_idx,
        "trial_index": trial_idx,
        "count": count,
        "planned_qubits": planned_qubits,
        "platform": platform,
        "platform_runtime_label": data.get("platform", platform),
        "algorithm": data.get("algorithm", "Unknown"),
        "backend_type": backend_type,
        "backend_name": backend_name,
        "is_fallback": is_fallback,
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


def mean_or_none(values: List[float]) -> Optional[float]:
    return statistics.mean(values) if values else None


def stats_with_ci(values: List[float]) -> Dict[str, Optional[float]]:
    n = len(values)
    if n == 0:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "std": None,
            "ci95_low": None,
            "ci95_high": None,
        }

    mean = statistics.mean(values)
    median = statistics.median(values)
    if n < 2:
        std = 0.0
        ci95_low = mean
        ci95_high = mean
    else:
        std = statistics.stdev(values)
        margin = 1.96 * (std / math.sqrt(n))
        ci95_low = mean - margin
        ci95_high = mean + margin

    return {
        "n": n,
        "mean": mean,
        "median": median,
        "std": std,
        "ci95_low": ci95_low,
        "ci95_high": ci95_high,
    }


def analysis_rows(rows: List[Dict[str, Any]], include_fallback: bool) -> List[Dict[str, Any]]:
    if include_fallback:
        return rows
    return [r for r in rows if not r.get("is_fallback", False)]


def scaling_exponent(success_rows: List[Dict[str, Any]]) -> Optional[float]:
    points = [(r["count"], r["execution_time_s"]) for r in success_rows if r["execution_time_s"] > 0]
    if len(points) < 2:
        return None

    # Aggregate repeats into one mean timing per count.
    by_count: Dict[int, List[float]] = {}
    for count, timing in points:
        by_count.setdefault(int(count), []).append(float(timing))

    if len(by_count.keys()) < 2:
        return None

    ordered_counts = sorted(by_count.keys())
    x = np.log(np.array(ordered_counts, dtype=float))
    y = np.log(np.array([statistics.mean(by_count[c]) for c in ordered_counts], dtype=float))
    slope, _intercept = np.polyfit(x, y, 1)
    return float(slope)


def build_summary(rows: List[Dict[str, Any]], counts: List[int], include_fallback: bool) -> Dict[str, Any]:
    analyzed_rows = analysis_rows(rows, include_fallback)
    summary: Dict[str, Any] = {
        "analysis": {
            "include_fallback": include_fallback,
            "rows_total": len(rows),
            "rows_analyzed": len(analyzed_rows),
            "rows_excluded_as_fallback": len(rows) - len(analyzed_rows),
        },
        "platforms": {},
        "speedups_vs_cpu": {},
        "qpu_qubit_scaling": {},
    }

    for platform in PLATFORMS:
        all_rows = platform_rows(rows, platform)
        analyzed_platform_rows = platform_rows(analyzed_rows, platform)
        success = successful_rows(analyzed_rows, platform)
        failures = [r for r in analyzed_platform_rows if not r["success"]]
        fallback_total = sum(1 for r in all_rows if r.get("is_fallback", False))
        fallback_excluded = sum(
            1 for r in all_rows if r.get("is_fallback", False) and not include_fallback
        )

        times = [float(r["execution_time_s"]) for r in success]
        throughputs = [float(r["throughput_numbers_per_s"]) for r in success]
        memories = [r["peak_memory_mb"] for r in success if r["peak_memory_mb"] is not None]
        time_stats = stats_with_ci(times)
        throughput_stats = stats_with_ci(throughputs)

        summary["platforms"][platform] = {
            "runs_total": len(all_rows),
            "runs_analyzed": len(analyzed_platform_rows),
            "runs_success": len(success),
            "runs_failed": len(failures),
            "fallback_runs_total": fallback_total,
            "fallback_runs_excluded": fallback_excluded,
            "mean_time_s": time_stats["mean"],
            "median_time_s": time_stats["median"],
            "std_time_s": time_stats["std"],
            "ci95_time_s_low": time_stats["ci95_low"],
            "ci95_time_s_high": time_stats["ci95_high"],
            "mean_throughput_numbers_per_s": throughput_stats["mean"],
            "median_throughput_numbers_per_s": throughput_stats["median"],
            "std_throughput_numbers_per_s": throughput_stats["std"],
            "ci95_throughput_numbers_per_s_low": throughput_stats["ci95_low"],
            "ci95_throughput_numbers_per_s_high": throughput_stats["ci95_high"],
            "best_throughput_numbers_per_s": max(throughputs) if throughputs else None,
            "mean_peak_memory_mb": mean_or_none(memories),
            "empirical_time_exponent": scaling_exponent(success),
            "backend_types": sorted({str(r.get("backend_type", "unknown")) for r in analyzed_platform_rows}),
            "notes": sorted({r["platform_runtime_label"] for r in analyzed_platform_rows}),
        }

    # Per-count speedups relative to CPU using mean timing across repeats.
    for count in counts:
        summary["speedups_vs_cpu"][str(count)] = {}
        cpu_rows = [
            r
            for r in analyzed_rows
            if r["count"] == count and r["platform"] == "CPU" and r["success"] and r["execution_time_s"] > 0
        ]
        if not cpu_rows:
            continue
        cpu_mean = statistics.mean([float(r["execution_time_s"]) for r in cpu_rows])

        for platform in ["GPU", "QPU"]:
            other_rows = [
                r
                for r in analyzed_rows
                if r["count"] == count
                and r["platform"] == platform
                and r["success"]
                and r["execution_time_s"] > 0
            ]
            if not other_rows:
                continue
            other_mean = statistics.mean([float(r["execution_time_s"]) for r in other_rows])
            if other_mean > 0:
                summary["speedups_vs_cpu"][str(count)][platform] = cpu_mean / other_mean

    qpu_success = successful_rows(analyzed_rows, "QPU")
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
        "trial_index",
        "count",
        "planned_qubits",
        "platform",
        "platform_runtime_label",
        "algorithm",
        "backend_type",
        "backend_name",
        "is_fallback",
        "included_in_analysis",
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
    repeats: int,
    warmup: int,
    include_fallback: bool,
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
    lines.append(f"- Measured repeats per workload: {repeats}")
    lines.append(f"- Warmup runs per workload: {warmup}")
    lines.append(f"- Include fallback runs in analysis: {include_fallback}")
    lines.append("")
    lines.append("## Problem Framing")
    lines.append(
        "Performance and resource efficiency comparison of Focus Algorithm RNG across CPU (O(N)), "
        "GPU (O(N/P)), and QPU with logarithmic qubit representation."
    )
    lines.append("")
    lines.append("## Platform Summary")
    lines.append("")
    lines.append("| Platform | Success/Analyzed/Total | Mean Time (s) | Std Time (s) | 95% CI Time (s) | Mean Throughput (/s) | Fallback Excluded | Empirical Time Exponent |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for platform in PLATFORMS:
        item = summary["platforms"].get(platform, {})
        ci_time = "N/A"
        if item.get("ci95_time_s_low") is not None and item.get("ci95_time_s_high") is not None:
            ci_time = f"[{_fmt(item.get('ci95_time_s_low'))}, {_fmt(item.get('ci95_time_s_high'))}]"
        lines.append(
            f"| {platform} | {item.get('runs_success', 0)}/{item.get('runs_analyzed', 0)}/{item.get('runs_total', 0)} | "
            f"{_fmt(item.get('mean_time_s'))} | {_fmt(item.get('std_time_s'))} | {ci_time} | "
            f"{_fmt(item.get('mean_throughput_numbers_per_s'))} | {item.get('fallback_runs_excluded', 0)} | "
            f"{_fmt(item.get('empirical_time_exponent'))} |"
        )
    lines.append("")

    lines.append("## Speedup vs CPU")
    lines.append("")
    lines.append("Speedups are computed from mean execution time across analyzed repeats per workload.")
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

    analysis_meta = summary.get("analysis", {})
    lines.append("## Analysis Filtering")
    lines.append("")
    lines.append(
        f"- Rows analyzed: {analysis_meta.get('rows_analyzed', 0)} / {analysis_meta.get('rows_total', 0)}"
    )
    lines.append(
        f"- Rows excluded as fallback: {analysis_meta.get('rows_excluded_as_fallback', 0)}"
    )
    lines.append("")

    failed = [r for r in rows if not r["success"]]
    if failed:
        lines.append("## Failures")
        lines.append("")
        lines.append("| Count | Trial | Platform | Error |")
        lines.append("| --- | --- | --- | --- |")
        for row in failed:
            error = str(row.get("error", "")).replace("|", "/")
            lines.append(f"| {row['count']} | {row.get('trial_index', 'N/A')} | {row['platform']} | {error} |")
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
    if args.repeats < 1:
        raise ValueError("--repeats must be >= 1")
    if args.warmup < 0:
        raise ValueError("--warmup must be >= 0")

    out_dir = Path(args.output_dir) if args.output_dir else (
        Path("results") / "reports" / f"focus_rng_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("Focus RNG Benchmark")
    print("=" * 80)
    print(f"Counts: {counts}")
    print(f"Qubit mode: {args.qubit_mode}")
    print(f"Repeats: {args.repeats}")
    print(f"Warmup runs: {args.warmup}")
    print(f"Include fallback in analysis: {args.include_fallback}")
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

        if args.warmup > 0:
            for warm_idx in range(1, args.warmup + 1):
                warm_seed = args.seed + warm_idx - 1
                warm_algo = RNGAlgorithm(count=count, num_qubits=qubits, seed=warm_seed)
                _ = warm_algo.run_comparison(platforms=PLATFORMS, shots=args.shots)
            print(f"  Warmup complete: {args.warmup} run(s) per platform")

        for trial_idx in range(1, args.repeats + 1):
            trial_seed = args.seed + trial_idx - 1
            print(f"  Trial {trial_idx}/{args.repeats} (seed={trial_seed})")

            algo = RNGAlgorithm(count=count, num_qubits=qubits, seed=trial_seed)
            result = algo.run_comparison(platforms=PLATFORMS, shots=args.shots)
            raw_results.append(
                {
                    "count": count,
                    "num_qubits": qubits,
                    "trial_index": trial_idx,
                    "seed": trial_seed,
                    "phase": "measured",
                    "result": result,
                }
            )

            for platform in PLATFORMS:
                data = result.get("platforms", {}).get(platform, {})
                row = extract_row(
                    run_idx=idx,
                    trial_idx=trial_idx,
                    count=count,
                    planned_qubits=qubits,
                    platform=platform,
                    data=data,
                )
                row["included_in_analysis"] = bool(
                    args.include_fallback or not row.get("is_fallback", False)
                )
                rows.append(row)
                if row["success"]:
                    fallback_note = " [FALLBACK]" if row.get("is_fallback") else ""
                    print(
                        f"    [OK] {platform}: time={row['execution_time_s']:.6f}s "
                        f"rate={row['throughput_numbers_per_s']:.2f}/s "
                        f"backend={row.get('backend_type', 'unknown')}{fallback_note}"
                    )
                else:
                    print(f"    [FAIL] {platform}: {row['error']}")

    rows_for_analysis = analysis_rows(rows, include_fallback=args.include_fallback)
    summary = build_summary(rows, counts, include_fallback=args.include_fallback)

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
                    "repeats": args.repeats,
                    "warmup": args.warmup,
                    "include_fallback": args.include_fallback,
                },
                "analysis": {
                    "rows_total": len(rows),
                    "rows_analyzed": len(rows_for_analysis),
                    "rows_excluded_as_fallback": len(rows) - len(rows_for_analysis),
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
        repeats=args.repeats,
        warmup=args.warmup,
        include_fallback=args.include_fallback,
        rows=rows,
        summary=summary,
    )

    if args.no_plots:
        print("\nSkipping plots (--no-plots set).")
    elif plt is None:
        print("\nSkipping plots (matplotlib is not installed).")
    else:
        plot_execution_time(rows_for_analysis, out_dir / "execution_time_vs_count.png")
        plot_resource_efficiency(rows_for_analysis, out_dir / "resource_efficiency.png")

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
        "--repeats",
        type=int,
        default=10,
        help="Number of measured repeats per workload (used for mean/std/CI).",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=2,
        help="Number of warmup runs per workload before measured repeats.",
    )
    parser.add_argument(
        "--include-fallback",
        action="store_true",
        help="Include fallback runs (e.g., GPU CPU-fallback) in analysis metrics.",
    )
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
    try:
        return run(args)
    except ValueError as exc:
        print(f"Argument error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
