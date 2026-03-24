# Comparative Analysis: Focus RNG (CPU vs GPU vs QPU)

This repository is now streamlined to one problem statement:

**Compare the performance and resource efficiency of RNG across CPU, GPU, and QPU architectures** using:

- execution time
- throughput
- memory usage in MB (CPU/GPU)
- qubit count (QPU)
- scaling behavior with workload size `N`

## What This Repo Contains

Primary files:

- `app.py`: Streamlit dashboard (primary interface)
- `focus_rng_benchmark.py`: batch benchmark + report generator
- `main.py`: minimal CLI runner for one RNG comparison
- `algorithms/rng_algorithm.py`: unified CPU/GPU/QPU RNG wrapper
- `quantum/quantum_rng.py`: Qiskit-based quantum RNG implementation
- `utils/helpers.py`: seed/device utility helpers
- `requirements.txt`: dependencies for this focused scope
- `run_dashboard.bat`: Windows launcher for dashboard

Documentation:

- `docs/DETAILED_DOCUMENTATION.md`: full technical walkthrough
- `docs/VIVA_PREP_QA.md`: viva Q&A prep

## Setup

Recommended Python version: **3.11**

### Linux/macOS

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Environment Variable

Create `.env` from template:

```bash
cp .env.example .env
```

Set token if you plan IBM backend usage:

```env
IBM_QUANTUM_TOKEN=your_token_here
```

## Run Options

## 1) Primary App (Dashboard)

```bash
streamlit run app.py
```

Windows helper:

```bat
run_dashboard.bat
```

Dashboard features:

- workload sweep over `N`
- CPU/GPU/QPU comparison
- execution-time and throughput scaling charts
- resource chart (MB vs qubits)
- speedup table vs CPU
- raw data view + download
- save artifacts to `results/reports/focus_rng_dashboard_<timestamp>/`

## 2) Batch Benchmark (Report Generator)

```bash
python focus_rng_benchmark.py
```

Example:

```bash
python focus_rng_benchmark.py \
  --counts 100,1000,5000,10000 \
  --qubit-mode logn \
  --max-qubits 10 \
  --shots 1024 \
  --warmup 2 \
  --repeats 10
```

Methodology notes:

- `--warmup` runs are executed before measured trials to stabilize timing.
- `--repeats` controls measured trials used for mean/std/95% CI.
- GPU CPU-fallback runs are excluded from primary analysis by default.
- Use `--include-fallback` only when you intentionally want fallback runs in summary/speedup metrics.

Output folder:

- `results/reports/focus_rng_<timestamp>/`

Generated files:

- `raw_runs.json`
- `results.csv`
- `summary.json`
- `report.md`
- `execution_time_vs_count.png`
- `resource_efficiency.png`

## 3) Minimal CLI Single Run

```bash
python main.py --count 1000 --qubits 8 --shots 1024 --seed 42
```

## Dependency Notes

- CPU baseline: `numpy` (+ optional `psutil` for memory metrics)
- GPU path: `torch` + CUDA for true GPU execution
- QPU path: `qiskit` + `qiskit-aer` (and optional IBM runtime)
- If dependencies are missing, platform-specific errors are reported clearly.
- Dashboard charts use `plotly`; if it is missing, the app now falls back to basic Streamlit charts.

## Troubleshooting

### `ModuleNotFoundError` (for `plotly`, `torch`, `qiskit`, `psutil`, etc.)

This means dependencies are not installed in the Python environment you are using to run the app.

1. Activate the project venv.
2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Verify imports in the same environment:

```bash
python -c "import plotly, torch, qiskit, psutil; print('ok')"
```

## Output Locations

- Dashboard artifacts: `results/reports/focus_rng_dashboard_<timestamp>/`
- Batch artifacts: `results/reports/focus_rng_<timestamp>/`

## Team Workflow (Git)

To avoid conflicts when multiple people contribute:

1. Update `main`

```bash
git checkout main
git pull origin main
```

2. Create branch from `main`

```bash
git checkout -b feature/<short-description>
```

3. Commit and push

```bash
git add .
git commit -m "Describe your change"
git push -u origin feature/<short-description>
```

4. Open PR from `feature/<short-description>` to `main`.
