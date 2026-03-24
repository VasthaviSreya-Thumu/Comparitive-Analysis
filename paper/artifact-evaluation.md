# Artifact Evaluation Guide

## Goal
Reproduce the key manuscript results and verify that generated paper tables/figures match benchmark artifacts.

## Prerequisites
1. Python environment initialized (`.venv`).
2. Dependencies installed:
```bash
.venv/bin/pip install -r requirements.txt
```
3. Writable matplotlib config path:
```bash
export MPLCONFIGDIR=/tmp/mpl
```

## Evaluation Steps

## Step 1: Re-run Main Benchmark
```bash
MPLCONFIGDIR=/tmp/mpl .venv/bin/python focus_rng_benchmark.py \
  --counts 64,128,256,512,1024 \
  --qubit-mode logn \
  --shots 1024 \
  --warmup 2 \
  --repeats 5 \
  --output-dir results/reports/paper_main
```

Pass condition:
- `results/reports/paper_main/summary.json` exists and includes:
  - `analysis.rows_total = 75`
  - `analysis.rows_excluded_as_fallback = 25` (in current non-CUDA environment)

## Step 2: Re-run Fallback Ablation
```bash
MPLCONFIGDIR=/tmp/mpl .venv/bin/python focus_rng_benchmark.py \
  --counts 64,128,256,512,1024 \
  --qubit-mode logn \
  --shots 1024 \
  --warmup 2 \
  --repeats 5 \
  --include-fallback \
  --no-plots \
  --output-dir results/reports/paper_ablation_include_fallback
```

Pass condition:
- `analysis.rows_excluded_as_fallback = 0`
- `GPU` speedup values are present in `speedups_vs_cpu`.

## Step 3: Re-run Fixed-Qubit Ablation
```bash
MPLCONFIGDIR=/tmp/mpl .venv/bin/python focus_rng_benchmark.py \
  --counts 64,128,256,512,1024 \
  --qubit-mode fixed \
  --fixed-qubits 10 \
  --shots 1024 \
  --warmup 2 \
  --repeats 5 \
  --no-plots \
  --output-dir results/reports/paper_ablation_fixedq
```

Pass condition:
- `qpu_qubit_scaling.mean_qubits = 10` in `summary.json`.

## Step 4: Regenerate Paper Tables/Figures
Use the same generation script pattern that writes:
- `paper/tables/table_main_platform_summary.csv`
- `paper/tables/table_main_speedup_vs_cpu.csv`
- `paper/tables/table_ablation_fallback_speedup.csv`
- `paper/tables/table_ablation_qubit_mode.csv`
- `paper/figures/fig_ablation_fallback_effect.png`
- `paper/figures/fig_ablation_qubit_mode.png`

Pass condition:
- Generated files exist and values are consistent with source `summary.json` files.

## Step 5: Traceability Verification
Open `paper/traceability-matrix.md` and verify every meaningful source file/artifact has at least one mapped manuscript section.

Pass condition:
- No meaningful repository component is unmapped.

## Expected Qualitative Outcomes (Current Environment)
- CPU results available.
- GPU rows marked as fallback (`cpu-fallback`) and excluded in primary analysis.
- QPU rows available with backend `simulator`.
- QPU mean runtime much higher than CPU for tested N.

## Evaluation Notes
- If CUDA becomes available, primary `GPU` analyzed rows should become non-zero and conclusions may change.
- If real IBM backend is configured, QPU backend labels and timings may significantly differ.
