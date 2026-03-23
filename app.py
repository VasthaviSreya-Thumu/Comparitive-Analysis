"""
Focus RNG Streamlit Dashboard

Compares RNG performance across:
- CPU: Sequential pseudo-RNG
- GPU: Parallel pseudo-RNG
- QPU: True quantum RNG

The dashboard is intentionally aligned to the project problem statement:
execution-time vs resource-efficiency (MB for CPU/GPU vs qubits for QPU),
plus scaling behavior against workload size.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    PLOTLY_AVAILABLE = True
    PLOTLY_IMPORT_ERROR: Optional[Exception] = None
except ModuleNotFoundError as exc:
    px = None
    go = None
    make_subplots = None
    PLOTLY_AVAILABLE = False
    PLOTLY_IMPORT_ERROR = exc

from algorithms.rng_algorithm import RNGAlgorithm
from utils.helpers import get_device_info, set_seed


PLATFORMS = ["CPU", "GPU", "QPU"]


st.set_page_config(
    page_title="Focus RNG Benchmark",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .main-header {
        font-size: 2.4rem;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #3b3b3b;
        margin-bottom: 1.0rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


def parse_counts(raw: str) -> List[int]:
    values: List[int] = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        value = int(token)
        if value <= 0:
            raise ValueError(f"Count must be > 0. Found: {value}")
        values.append(value)
    if not values:
        raise ValueError("At least one workload size is required.")
    return sorted(set(values))


def resolve_qubits(
    count: int,
    mode: str,
    fixed_qubits: int,
    min_qubits: int,
    max_qubits: int,
) -> int:
    if mode == "fixed":
        return fixed_qubits

    recommended = int(math.ceil(math.log2(max(2, count))))
    return max(min_qubits, min(max_qubits, recommended))


def extract_run_row(
    sweep_idx: int,
    count: int,
    planned_qubits: int,
    platform: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    success = bool(data.get("success", False))
    execution_time = float(data.get("generation_time", 0.0) or 0.0)
    throughput = float(data.get("numbers_per_second", 0.0) or 0.0)

    peak_memory = data.get("peak_memory_mb")
    if peak_memory is None:
        peak_memory = data.get("memory_used_mb")
    peak_memory = float(peak_memory) if peak_memory is not None else None

    qpu_qubits = None
    if platform == "QPU":
        qpu_qubits = int(data.get("num_qubits", planned_qubits) or planned_qubits)

    return {
        "sweep_idx": sweep_idx,
        "count": int(count),
        "planned_qubits": int(planned_qubits),
        "platform": platform,
        "platform_runtime_label": data.get("platform", platform),
        "algorithm": data.get("algorithm", "Unknown"),
        "success": success,
        "error": str(data.get("error", "")),
        "execution_time_s": execution_time,
        "throughput_numbers_per_s": throughput,
        "peak_memory_mb": peak_memory,
        "qpu_qubits": qpu_qubits,
    }


def successful_rows(rows: List[Dict[str, Any]], platform: str) -> List[Dict[str, Any]]:
    return [r for r in rows if r["platform"] == platform and r["success"] and r["execution_time_s"] > 0]


def _mean(values: List[float]) -> Optional[float]:
    return float(np.mean(values)) if values else None


def _median(values: List[float]) -> Optional[float]:
    return float(np.median(values)) if values else None


def _fmt(value: Optional[float], precision: int = 4) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{precision}f}"


def empirical_time_exponent(rows: List[Dict[str, Any]], platform: str) -> Optional[float]:
    sr = successful_rows(rows, platform)
    if len(sr) < 2:
        return None

    by_count: Dict[int, float] = {}
    for row in sr:
        by_count[row["count"]] = row["execution_time_s"]
    if len(by_count) < 2:
        return None

    x = np.log(np.array(list(by_count.keys()), dtype=float))
    y = np.log(np.array(list(by_count.values()), dtype=float))
    slope, _ = np.polyfit(x, y, 1)
    return float(slope)


def speedups_vs_cpu(rows: List[Dict[str, Any]], counts: List[int]) -> pd.DataFrame:
    index: List[Dict[str, Any]] = []

    for count in counts:
        cpu = next(
            (
                r
                for r in rows
                if r["count"] == count and r["platform"] == "CPU" and r["success"] and r["execution_time_s"] > 0
            ),
            None,
        )
        if cpu is None:
            index.append({"count": count, "gpu_speedup_vs_cpu": None, "qpu_speedup_vs_cpu": None})
            continue

        gpu = next(
            (
                r
                for r in rows
                if r["count"] == count and r["platform"] == "GPU" and r["success"] and r["execution_time_s"] > 0
            ),
            None,
        )
        qpu = next(
            (
                r
                for r in rows
                if r["count"] == count and r["platform"] == "QPU" and r["success"] and r["execution_time_s"] > 0
            ),
            None,
        )

        index.append(
            {
                "count": count,
                "gpu_speedup_vs_cpu": (cpu["execution_time_s"] / gpu["execution_time_s"]) if gpu else None,
                "qpu_speedup_vs_cpu": (cpu["execution_time_s"] / qpu["execution_time_s"]) if qpu else None,
            }
        )

    return pd.DataFrame(index)


def summarize(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    out = []
    for platform in PLATFORMS:
        prs = [r for r in rows if r["platform"] == platform]
        ok = successful_rows(rows, platform)
        times = [r["execution_time_s"] for r in ok]
        tps = [r["throughput_numbers_per_s"] for r in ok]
        memories = [r["peak_memory_mb"] for r in ok if r["peak_memory_mb"] is not None]

        out.append(
            {
                "platform": platform,
                "success_runs": len(ok),
                "total_runs": len(prs),
                "mean_time_s": _mean(times),
                "median_time_s": _median(times),
                "mean_throughput_numbers_per_s": _mean(tps),
                "mean_peak_memory_mb": _mean(memories),
                "empirical_time_exponent": empirical_time_exponent(rows, platform),
            }
        )
    return pd.DataFrame(out)


def run_benchmark(
    counts: List[int],
    qubit_mode: str,
    fixed_qubits: int,
    min_qubits: int,
    max_qubits: int,
    shots: int,
    seed: int,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    set_seed(seed)
    rows: List[Dict[str, Any]] = []
    raw_runs: List[Dict[str, Any]] = []

    status = st.empty()
    progress = st.progress(0)
    total = len(counts)

    for idx, count in enumerate(counts, start=1):
        qubits = resolve_qubits(
            count=count,
            mode=qubit_mode,
            fixed_qubits=fixed_qubits,
            min_qubits=min_qubits,
            max_qubits=max_qubits,
        )
        status.text(f"Running benchmark {idx}/{total}: N={count}, qubits={qubits}")

        algo = RNGAlgorithm(count=count, num_qubits=qubits, seed=seed)
        result = algo.run_comparison(platforms=PLATFORMS, shots=shots)
        raw_runs.append({"count": count, "num_qubits": qubits, "result": result})

        for platform in PLATFORMS:
            data = result.get("platforms", {}).get(platform, {})
            rows.append(extract_run_row(idx, count, qubits, platform, data))

        progress.progress(int((idx / total) * 100))

    status.empty()
    progress.empty()
    return rows, raw_runs


def line_chart(df: pd.DataFrame, y_col: str, title: str, y_label: str) -> go.Figure:
    fig = px.line(
        df[df["success"]].sort_values("count"),
        x="count",
        y=y_col,
        color="platform",
        markers=True,
        title=title,
        log_x=True,
    )
    fig.update_layout(xaxis_title="Count (N)", yaxis_title=y_label)
    return fig


def resource_dual_axis_chart(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for platform in ["CPU", "GPU"]:
        subset = df[(df["platform"] == platform) & (df["success"])].sort_values("count")
        fig.add_trace(
            go.Scatter(
                x=subset["count"],
                y=subset["peak_memory_mb"],
                mode="lines+markers",
                name=f"{platform} Memory (MB)",
            ),
            secondary_y=False,
        )

    qpu = df[(df["platform"] == "QPU") & (df["success"])].sort_values("count")
    fig.add_trace(
        go.Scatter(
            x=qpu["count"],
            y=qpu["qpu_qubits"],
            mode="lines+markers",
            name="QPU Qubits",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="Resource Efficiency: Memory (MB) vs Qubit Count",
        xaxis_title="Count (N)",
        xaxis_type="log",
    )
    fig.update_yaxes(title_text="Peak Memory (MB)", secondary_y=False)
    fig.update_yaxes(title_text="Qubit Count", secondary_y=True)
    return fig


def time_vs_resource_scatter(df: pd.DataFrame) -> go.Figure:
    # Unified resource axis for conceptual comparison:
    # CPU/GPU use MB, QPU uses qubits.
    chart_df = df[df["success"]].copy()
    chart_df["resource_value"] = chart_df.apply(
        lambda r: r["peak_memory_mb"] if r["platform"] in ("CPU", "GPU") else r["qpu_qubits"],
        axis=1,
    )
    chart_df["resource_unit"] = chart_df.apply(
        lambda r: "MB" if r["platform"] in ("CPU", "GPU") else "Qubits",
        axis=1,
    )

    fig = px.scatter(
        chart_df,
        x="resource_value",
        y="execution_time_s",
        color="platform",
        symbol="resource_unit",
        hover_data=["count", "throughput_numbers_per_s", "resource_unit"],
        title="Execution Time vs Resource Footprint (MB for CPU/GPU, Qubits for QPU)",
    )
    fig.update_layout(xaxis_title="Resource Footprint", yaxis_title="Execution Time (s)")
    return fig


def save_run_artifacts(
    rows_df: pd.DataFrame,
    raw_runs: List[Dict[str, Any]],
    summary_df: pd.DataFrame,
    speedups_df: pd.DataFrame,
) -> Path:
    out_dir = Path("results") / "reports" / f"focus_rng_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "raw_runs.json").write_text(json.dumps(raw_runs, indent=2), encoding="utf-8")
    rows_df.to_csv(out_dir / "results.csv", index=False)
    summary_df.to_csv(out_dir / "summary.csv", index=False)
    speedups_df.to_csv(out_dir / "speedups_vs_cpu.csv", index=False)

    return out_dir


def render_sidebar() -> Dict[str, Any]:
    st.sidebar.title("Focus RNG Controls")

    st.sidebar.markdown("### System")
    info = get_device_info()
    st.sidebar.markdown(f"- CPU Threads: **{info.get('cpu_count', 'N/A')}**")
    st.sidebar.markdown(f"- CUDA Available: **{info.get('cuda_available', False)}**")
    if info.get("gpu_available"):
        st.sidebar.markdown(f"- GPU: **{info.get('gpu_name', 'Unknown')}**")
    else:
        st.sidebar.warning("GPU not detected or unavailable. GPU path may fallback to CPU.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Benchmark Setup")

    counts_raw = st.sidebar.text_input("Workload sizes N (comma-separated)", value="100,1000,5000,10000")
    qubit_mode = st.sidebar.selectbox("Qubit selection mode", ["logn", "fixed"], index=0)

    fixed_qubits = st.sidebar.slider("Fixed qubits", min_value=2, max_value=16, value=8)
    min_qubits = st.sidebar.slider("Min qubits (logn mode)", min_value=2, max_value=16, value=2)
    max_qubits = st.sidebar.slider("Max qubits (logn mode)", min_value=2, max_value=16, value=10)
    shots = st.sidebar.slider("Quantum shots", min_value=128, max_value=4096, step=128, value=1024)
    seed = st.sidebar.number_input("Random seed", min_value=0, max_value=999999, value=42)

    run_clicked = st.sidebar.button("Run Focus RNG Benchmark", type="primary")
    return {
        "counts_raw": counts_raw,
        "qubit_mode": qubit_mode,
        "fixed_qubits": fixed_qubits,
        "min_qubits": min_qubits,
        "max_qubits": max_qubits,
        "shots": shots,
        "seed": int(seed),
        "run_clicked": run_clicked,
    }


def main() -> None:
    st.markdown('<div class="main-header">Focus RNG Architecture Comparison</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">CPU (Sequential Pseudo-RNG) vs GPU (Parallel Pseudo-RNG) vs QPU (True Quantum RNG)</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "This app is purpose-built for your problem statement: compare execution time and "
        "resource efficiency (MB vs qubits) and inspect scaling from O(N), O(N/P), and log2(N)-style qubit growth."
    )

    if "rows_df" not in st.session_state:
        st.session_state.rows_df = None
    if "raw_runs" not in st.session_state:
        st.session_state.raw_runs = None

    params = render_sidebar()

    if params["run_clicked"]:
        try:
            counts = parse_counts(params["counts_raw"])
        except Exception as exc:
            st.error(f"Invalid counts input: {exc}")
            return

        rows, raw_runs = run_benchmark(
            counts=counts,
            qubit_mode=params["qubit_mode"],
            fixed_qubits=params["fixed_qubits"],
            min_qubits=params["min_qubits"],
            max_qubits=params["max_qubits"],
            shots=params["shots"],
            seed=params["seed"],
        )
        st.session_state.rows_df = pd.DataFrame(rows)
        st.session_state.raw_runs = raw_runs

    df: Optional[pd.DataFrame] = st.session_state.rows_df
    if df is None or df.empty:
        st.markdown("### Ready to Run")
        st.write("Configure settings in the sidebar and click **Run Focus RNG Benchmark**.")
        return

    summary_df = summarize(df.to_dict(orient="records"))
    counts = sorted(df["count"].unique().tolist())
    speedups_df = speedups_vs_cpu(df.to_dict(orient="records"), counts)

    if not PLOTLY_AVAILABLE:
        st.warning(
            "Plotly is not installed in this environment. Showing fallback charts. "
            "Install full dependencies with: `pip install -r requirements.txt`"
        )
        if PLOTLY_IMPORT_ERROR:
            st.caption(f"Plotly import error: {PLOTLY_IMPORT_ERROR}")

    st.markdown("### Platform Summary")
    c1, c2, c3 = st.columns(3)
    for idx, platform in enumerate(PLATFORMS):
        row = summary_df[summary_df["platform"] == platform].iloc[0]
        target = [c1, c2, c3][idx]
        with target:
            st.markdown(f"#### {platform}")
            st.metric("Successful runs", f"{int(row['success_runs'])}/{int(row['total_runs'])}")
            st.metric("Mean time (s)", _fmt(row["mean_time_s"], 6))
            st.metric("Mean throughput (/s)", _fmt(row["mean_throughput_numbers_per_s"], 2))
            if platform in ("CPU", "GPU"):
                st.metric("Mean peak memory (MB)", _fmt(row["mean_peak_memory_mb"], 3))
            else:
                qpu_ok = df[(df["platform"] == "QPU") & (df["success"])]
                mean_qubits = float(qpu_ok["qpu_qubits"].mean()) if not qpu_ok.empty else None
                st.metric("Mean qubits", _fmt(mean_qubits, 2))

    st.markdown("---")
    t1, t2, t3, t4 = st.tabs(
        [
            "Execution Time Scaling",
            "Resource Efficiency",
            "Speedups & Complexity",
            "Raw Data",
        ]
    )

    with t1:
        if PLOTLY_AVAILABLE:
            st.plotly_chart(
                line_chart(
                    df,
                    y_col="execution_time_s",
                    title="Execution Time vs Count",
                    y_label="Execution Time (s)",
                ),
                use_container_width=True,
            )
            st.plotly_chart(
                line_chart(
                    df,
                    y_col="throughput_numbers_per_s",
                    title="Throughput vs Count",
                    y_label="Numbers per second",
                ),
                use_container_width=True,
            )
        else:
            st.markdown("#### Execution Time vs Count")
            time_df = (
                df[df["success"]]
                .pivot_table(index="count", columns="platform", values="execution_time_s", aggfunc="mean")
                .sort_index()
            )
            st.line_chart(time_df)

            st.markdown("#### Throughput vs Count")
            thr_df = (
                df[df["success"]]
                .pivot_table(index="count", columns="platform", values="throughput_numbers_per_s", aggfunc="mean")
                .sort_index()
            )
            st.line_chart(thr_df)

    with t2:
        if PLOTLY_AVAILABLE:
            st.plotly_chart(resource_dual_axis_chart(df), use_container_width=True)
            st.plotly_chart(time_vs_resource_scatter(df), use_container_width=True)
        else:
            st.markdown("#### Resource Efficiency (Fallback View)")
            cpu_gpu_mem = (
                df[(df["success"]) & (df["platform"].isin(["CPU", "GPU"]))]
                .pivot_table(index="count", columns="platform", values="peak_memory_mb", aggfunc="mean")
                .sort_index()
            )
            if not cpu_gpu_mem.empty:
                st.caption("CPU/GPU Peak Memory (MB)")
                st.line_chart(cpu_gpu_mem)

            qpu_qubits = (
                df[(df["success"]) & (df["platform"] == "QPU")]
                .pivot_table(index="count", values="qpu_qubits", aggfunc="mean")
                .sort_index()
            )
            if not qpu_qubits.empty:
                st.caption("QPU Qubit Count")
                st.line_chart(qpu_qubits)

            st.caption("Execution time vs resource table")
            fallback_table = df[df["success"]][
                ["count", "platform", "execution_time_s", "peak_memory_mb", "qpu_qubits"]
            ].sort_values(["count", "platform"])
            st.dataframe(fallback_table, use_container_width=True)

    with t3:
        st.markdown("#### Speedup vs CPU by Workload Size")
        st.dataframe(speedups_df, use_container_width=True)

        st.markdown("#### Empirical Scaling Notes")
        st.write("- CPU expected complexity: `O(N)`")
        st.write("- GPU expected complexity: `O(N/P)`")
        st.write("- QPU memory representation: approximately `O(log2(N))` qubits")
        st.dataframe(
            summary_df[["platform", "empirical_time_exponent"]].rename(
                columns={"empirical_time_exponent": "empirical_time_exponent_loglog"}
            ),
            use_container_width=True,
        )

        qpu_ok = df[(df["platform"] == "QPU") & (df["success"])].copy()
        if not qpu_ok.empty:
            qpu_ok["log2_count"] = np.log2(qpu_ok["count"])
            qpu_ok["qubit_to_log2n_ratio"] = qpu_ok["qpu_qubits"] / qpu_ok["log2_count"]
            st.markdown("#### QPU Qubit Scaling Check")
            st.dataframe(
                qpu_ok[["count", "qpu_qubits", "log2_count", "qubit_to_log2n_ratio"]],
                use_container_width=True,
            )

    with t4:
        st.markdown("#### Flattened Benchmark Table")
        st.dataframe(df, use_container_width=True)

        st.markdown("#### Download Data")
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            data=csv_data,
            file_name="focus_rng_results.csv",
            mime="text/csv",
        )
        json_data = json.dumps(st.session_state.raw_runs, indent=2).encode("utf-8")
        st.download_button(
            "Download Raw JSON",
            data=json_data,
            file_name="focus_rng_raw_runs.json",
            mime="application/json",
        )

        if st.button("Save Artifacts to results/reports"):
            out_dir = save_run_artifacts(df, st.session_state.raw_runs, summary_df, speedups_df)
            st.success(f"Saved artifacts to: {out_dir}")

    failures = df[~df["success"]]
    if not failures.empty:
        st.warning("Some runs failed. Review details below.")
        st.dataframe(
            failures[["count", "platform", "error"]],
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
