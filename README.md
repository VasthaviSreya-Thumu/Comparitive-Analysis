# Comparative Analysis: CPU vs GPU vs QPU Algorithms

This repository benchmarks the same high-level tasks across three compute models:

- CPU (classical sequential execution)
- GPU (classical parallel execution via PyTorch/CUDA)
- QPU (quantum simulation and optional IBM backend integration via Qiskit)

It includes:

- A CLI runner for experiments
- A Streamlit dashboard for interactive comparisons
- Implementations for Search, RNG, and Tic-Tac-Toe game simulation
- Monitoring and result-export utilities

What this project is:

- A benchmarking/experimental application
- Run as a CLI tool (`main.py`) or interactive dashboard (`app.py`)

What this project is not:

- Not a long-running backend service/API by default
- Not an ML model training or inference repository

## What The Repository Contains

### Top-level files

- `main.py`: CLI entry point to run comparisons (`search`, `rng`, `game`)
- `app.py`: Streamlit dashboard entry point
- `config.py`: project paths, defaults, and hardware detection
- `requirements.txt`: Python dependency list
- `PROFILING_DESCRIPTION.md`: conceptual notes for memory/energy profiling
- `run_dashboard.bat`: Windows helper to launch Streamlit dashboard

### Source folders

- `algorithms/`: unified wrappers + CPU/GPU/QPU implementations
  - `search_algorithm.py`, `cpu_search.py`, `gpu_search.py`, `qpu_search.py`
  - `rng_algorithm.py`
  - `game_algorithm.py`
- `quantum/`: quantum circuit implementations and runners
  - `grover_search.py`
  - `quantum_rng.py`
  - `quantum_game.py`
- `core/`:
  - `comparator.py`: orchestrates search experiments and saves outputs
  - `unified_monitor.py`: logs performance/memory metrics
- `utils/`:
  - `helpers.py`: seed setup, device detection, formatting helpers
- `tests/`:
  - `test_search.py`: integration-style script for search comparisons
- `results/`:
  - sample historical output JSON files under `results/data/`

## Architecture Overview

For each experiment type, the project follows this pattern:

1. Build a single problem definition (for example, one search dataset).
2. Execute on `CPU`, `GPU`, and `QPU` paths.
3. Collect normalized metrics (time, memory, throughput, success).
4. Render results in CLI or dashboard; optionally persist JSON logs.

### Implemented experiment types

- Search:
  - CPU: linear search `O(N)`
  - GPU: vectorized tensor comparison `O(N/P)` (with CUDA fallback behavior)
  - QPU: Grover-based search `O(sqrt(N))` on simulator/backend
- RNG:
  - CPU: NumPy pseudo-random generation
  - GPU: PyTorch parallel random generation
  - QPU: superposition-measurement-based quantum random generation
- Game (Tic-Tac-Toe simulation):
  - CPU: random sequential play
  - GPU: simplified parallel tensor simulation
  - QPU: quantum move selection per turn

## Environment And Prerequisites

- OS: Linux/macOS/Windows
- Python: 3.x (virtual environment strongly recommended)
- Optional hardware:
  - NVIDIA GPU with CUDA for true GPU execution
  - IBM Quantum account/token for real hardware experiments

## Installation

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

### Environment variables

Create a `.env` file (or update the existing one) for IBM access:

```env
IBM_QUANTUM_TOKEN=your_token_here
```

Important:

- Keep `.env` private; do not commit real tokens.
- Current code includes IBM backend handling in quantum modules, but the default search/game/rng paths run on simulator unless you pass/configure a backend explicitly in code.

### Code-level defaults (`config.py`)

- `DEFAULT_DATABASE_SIZE = 1000`
- `DATABASE_SIZES = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000]`
- `DEFAULT_SHOTS = 1024`
- `USE_REAL_QPU = False`
- Directories auto-created on import:
  - `results/`
  - `results/logs/`
  - `results/charts/`

## How To Run

Quick start (uses defaults):

```bash
python main.py
```

By default this runs the `search` comparison with default size (`1000`).  
Use flags only when you want to switch algorithm or override defaults.

### 1) CLI mode (`main.py`)

General pattern:

```bash
python main.py --algorithm <search|rng|game> [options]
```

Examples:

```bash
# Search comparison
python main.py --algorithm search --size 1000 --target 615

# RNG comparison (--size is used as count)
python main.py --algorithm rng --size 10000

# Game comparison
python main.py --algorithm game --games 20
```

CLI arguments:

- `--algorithm`: `search` (default), `rng`, `game`
- `--size`: search database size OR rng count
- `--target`: target position for search (optional)
- `--games`: number of Tic-Tac-Toe games
- `--test`: currently defined but not used by the implementation

### 2) Dashboard mode (`app.py`)

```bash
streamlit run app.py
```

Windows helper:

```bat
run_dashboard.bat
```

Dashboard capabilities:

- Choose algorithm and parameters from sidebar
- Run CPU/GPU/QPU comparison interactively
- Inspect time, memory, and throughput charts
- View raw JSON output in-page

### 3) Search test script

```bash
python tests/test_search.py
```

This is an integration script with printed summaries, not strict unit tests with assertions.

## Programmatic Usage

You can run the search comparator directly in Python:

```python
from core.comparator import ExperimentComparator

comparator = ExperimentComparator()
result = comparator.run_search_comparison(database_size=1000, target_position=615, monitor=True)
```

Batch mode:

```python
sizes = [100, 1000, 10000]
all_results = comparator.run_batch_size_comparison(sizes)
comparator.save_all_results("all_search_results.json")
```

## Outputs And Result Files

### Runtime outputs

Each run produces a result dictionary with:

- `platforms`: CPU/GPU/QPU metrics
- `success`/`error` per platform
- task-specific performance metrics

### Saved files

- `core/comparator.py` writes search JSON snapshots to:
  - `results/search_comparison_N<database_size>_<timestamp>.json`
- `core/unified_monitor.py` writes logs to:
  - `results/logs/search_metrics_<YYYYMMDD>.json`
- Existing sample data is present in:
  - `results/data/`

## Platform-Specific Behavior And Limits

### GPU path

- If CUDA is not available, GPU routines fallback to CPU simulation/fallback labels.
- Throughput and memory metrics in fallback mode do not represent true GPU hardware.

### QPU path

- Search uses qubit count `ceil(log2(N))` and expands search space to nearest power of two.
- QPU search currently defaults to simulator backend in `qpu_search.py`.
- RNG QPU path applies a soft cap `count <= 500000`.
- Game QPU path caps games at `5` for runtime control.

## Known Gaps / Caveats

- No packaged `pytest` test suite with assertions; current tests are script-style.
- `main.py` imports `ExperimentComparator` but currently runs algorithms directly.
- `--test` flag exists in CLI parser but has no dedicated behavior.
- `requirements.txt` includes broad dependencies; some may be unused for minimal execution.

## Troubleshooting

### `ModuleNotFoundError` (e.g., `torch`, `streamlit`)

Install dependencies:

```bash
pip install -r requirements.txt
```

### GPU not detected

- Confirm CUDA-enabled PyTorch is installed.
- Verify NVIDIA drivers and CUDA runtime.
- Check runtime output in CLI banner/device info.

### Slow QPU runs

- Quantum simulation cost rises quickly with qubits and shots.
- Reduce dataset size / qubits / shot count for faster iteration.

## Suggested Workflow For New Users

1. Install dependencies in a fresh virtual environment.
2. Run `python main.py --algorithm search --size 1000` to validate setup.
3. Launch `streamlit run app.py` for interactive analysis.
4. Review generated JSON in `results/` and sample artifacts in `results/data/`.

## Team Collaboration Workflow (Git)

When multiple people are working on this repo, do not push direct changes to `main`.  
Use a feature branch and raise a pull request.

1. Update local `main`:

```bash
git checkout main
git pull origin main
```

2. Create a branch from `main`:

```bash
git checkout -b feature/<short-description>
```

3. Make your changes, then commit:

```bash
git add .
git commit -m "Describe your change"
```

4. Push the branch:

```bash
git push -u origin feature/<short-description>
```

5. Open a Pull Request:

- Create a PR from `feature/<short-description>` -> `main`
- Ask for review before merge
- Merge only after approvals/checks pass

Why this helps:

- Keeps `main` stable
- Reduces merge conflicts
- Makes changes easier to review and track

## Notes On Profiling Document

`PROFILING_DESCRIPTION.md` explains conceptual memory/energy modeling across CPU/GPU/QPU. It is descriptive documentation; the current code primarily logs runtime/memory metrics.
