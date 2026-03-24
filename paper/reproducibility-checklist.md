# Reproducibility Checklist

## 1) Code and Versioning
- Repository root: `/home/rohith0109/projects/Comparitive-Analysis`
- Commit snapshot used for paper package generation: `b24582a`
- Local modifications present: yes (paper package + benchmarking updates)

## 2) Environment
- Python: `3.13.11`
- OS: `Linux-6.18.3-arch1-1-x86_64-with-glibc2.42`
- CPU: 8 logical / 4 physical cores
- CUDA available: `False`
- QPU backend in reported primary run: `aer_simulator`
- Full snapshot: `paper/tables/table_environment_snapshot.csv`

## 3) Dependencies
Install command:
```bash
.venv/bin/pip install -r requirements.txt
```

Key versions used:
- numpy 2.4.3
- pandas 2.3.3
- torch 2.11.0+cpu
- qiskit 2.3.1
- qiskit-aer 0.17.2
- streamlit 1.55.0
- plotly 6.6.0
- matplotlib 3.10.8

## 4) Runtime Configuration
- Set writable matplotlib cache path in restricted environments:
```bash
export MPLCONFIGDIR=/tmp/mpl
```

- Optional IBM runtime token path:
```bash
cp .env.example .env
# then set IBM_QUANTUM_TOKEN in .env
```

## 5) Main Experiment (Primary Results)
```bash
MPLCONFIGDIR=/tmp/mpl .venv/bin/python focus_rng_benchmark.py \
  --counts 64,128,256,512,1024 \
  --qubit-mode logn \
  --shots 1024 \
  --warmup 2 \
  --repeats 5 \
  --output-dir results/reports/paper_main
```

Expected artifacts:
- `results/reports/paper_main/raw_runs.json`
- `results/reports/paper_main/results.csv`
- `results/reports/paper_main/summary.json`
- `results/reports/paper_main/report.md`
- `results/reports/paper_main/execution_time_vs_count.png`
- `results/reports/paper_main/resource_efficiency.png`

## 6) Ablation Runs
### A) Include fallback rows
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

### B) Fixed-qubit policy
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

## 7) Determinism Controls
- Global seed argument: `--seed` (default `42`)
- Trial seeds increment as `seed + trial_index - 1`
- Warmup seeds increment similarly

## 8) Artifact Derivation for Manuscript
Tables/figures in `paper/` are derived from report artifacts with the generation script executed during this session.
Generated outputs:
- `paper/tables/*.csv`
- `paper/figures/*.png`
- `paper/figures/fig_pipeline_architecture.svg`

## 9) Known Reproducibility Risks
- GPU claims are environment-sensitive; current environment has no CUDA.
- QPU hardware claims require IBM backend credentials and available queue access.
- Matplotlib cache path may need explicit override (`MPLCONFIGDIR`).
