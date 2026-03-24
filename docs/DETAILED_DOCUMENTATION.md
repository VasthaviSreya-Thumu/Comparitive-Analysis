# Focus RNG Repository: Detailed Technical Documentation

## 1) Scope of the Repository

This repository has been intentionally reduced to support one objective:

**Benchmark RNG performance and resource efficiency across CPU, GPU, and QPU.**

Architectures compared:

- CPU: Sequential Pseudo-RNG
- GPU: Parallel Pseudo-RNG
- QPU: True Quantum RNG (Qiskit-based)

Metrics used:

- execution time
- throughput (numbers/sec)
- memory footprint (MB) for CPU/GPU
- qubit count for QPU
- scaling trend across workload sizes `N`

## 2) Current File-Level Architecture

## 2.1 Entry points

- `app.py`
  - Streamlit interactive benchmark dashboard
  - primary user-facing app

- `focus_rng_benchmark.py`
  - batch benchmark runner
  - generates machine-readable and human-readable reports

- `main.py`
  - lightweight one-shot CLI comparison

## 2.2 Core implementation files

- `algorithms/rng_algorithm.py`
  - unified wrapper that executes RNG on CPU, GPU, and QPU

- `quantum/quantum_rng.py`
  - Qiskit quantum RNG circuit and execution logic

- `utils/helpers.py`
  - reproducibility and device-info helpers

## 2.3 Supporting files

- `requirements.txt`
- `run_dashboard.bat`
- `.env.example`
- `README.md`
- `docs/VIVA_PREP_QA.md`

## 3) Runtime Flow

## 3.1 Dashboard (`app.py`) flow

1. User enters sweep settings in sidebar:
   - workload sizes `N`
   - qubit mode (`fixed` or `logn`)
   - shots
   - seed

2. `run_benchmark(...)` loops over each `N`.

3. For each workload:
   - derive qubit count (`resolve_qubits`)
   - call `RNGAlgorithm(...).run_comparison(platforms=[CPU, GPU, QPU])`

4. Platform outputs are flattened into tabular rows (`extract_run_row`).

5. App computes:
   - summary stats (`summarize`)
   - speedup vs CPU (`speedups_vs_cpu`)
   - empirical scaling exponent via log-log slope (`empirical_time_exponent`)

6. App renders charts and tables.

7. Optional save action writes artifacts to:
   - `results/reports/focus_rng_dashboard_<timestamp>/`

## 3.2 Batch benchmark (`focus_rng_benchmark.py`) flow

1. Parse CLI arguments.
2. For each workload size, run configurable warmups (`--warmup`).
3. Run configurable measured repeats (`--repeats`) for CPU/GPU/QPU.
4. Flatten results with trial index, backend type, and fallback flags.
5. Build summary aggregates with mean/std/95% CI and speedup table.
6. Exclude fallback runs (for example GPU CPU-fallback) from primary analysis by default.
7. Save:
   - `raw_runs.json`
   - `results.csv`
   - `summary.json`
   - `report.md`
   - plots (if matplotlib available)

Output folder:

- `results/reports/focus_rng_<timestamp>/`

## 3.3 Minimal CLI (`main.py`) flow

1. Parse one run configuration (`count`, `qubits`, `shots`, `seed`).
2. Print hardware summary (`get_device_info`).
3. Execute one `RNGAlgorithm.run_comparison(...)` call.
4. Print concise per-platform result summary.

## 4) Module Deep Dive

## 4.1 `algorithms/rng_algorithm.py`

### Class: `RNGAlgorithm`

Purpose: expose a common API for CPU/GPU/QPU RNG execution.

Constructor parameters:

- `count`: number of values to generate
- `num_qubits`: QPU bit-width
- `seed`: random seed for reproducibility (classical paths)

### Main methods

- `get_info()`
  - returns metadata (`count`, range, qubits)

- `run(platform, **kwargs)`
  - dispatches to `_run_cpu`, `_run_gpu`, `_run_qpu`

- `_run_cpu(...)`
  - uses NumPy `randint`
  - optionally captures memory via `psutil` if installed
  - returns timing, throughput, memory, and sample outputs

- `_run_gpu(...)`
  - uses PyTorch `torch.randint` on CUDA
  - captures peak GPU memory
  - if torch/CUDA unavailable: reuses CPU path and relabels as GPU fallback

- `_run_qpu(...)`
  - calls `quantum.quantum_rng.run_quantum_rng`
  - applies soft cap `count <= 500000`
  - returns qubit-aware metrics

- `run_comparison(platforms=None, **kwargs)`
  - loops over requested platforms
  - returns unified dictionary with success/error details per platform

### Returned schema (platform row)

Common fields:

- `platform`
- `algorithm`
- `backend_type`
- `is_fallback`
- `success`
- `generation_time`
- `numbers_per_second`
- `peak_memory_mb` (classical, approximate for qpu wrapper)
- `error` (only on failure)

QPU-specific additional field:

- `num_qubits`
- `backend_name`

## 4.2 `quantum/quantum_rng.py`

### Class: `QuantumRNG`

Purpose: build and run a quantum random number generation circuit.

Circuit logic:

- initialize `num_qubits` register
- apply Hadamard on all qubits (uniform superposition)
- measure all qubits

### Key functions

- `build_circuit()`
  - returns the Hadamard+measurement circuit

- `generate_random_numbers(count, backend=None, shots=1)`
  - if IBM backend:
    - runs SamplerV2 and extracts bitstrings
  - else (Aer simulator):
    - runs a **single batched job** with `memory=True`
    - extracts bitstrings directly
    - this is a key optimization over per-number job submission

- `run_quantum_rng(...)`
  - orchestration function returning:
    - generated numbers
    - statistics (mean/std/min/max/uniformity score)
    - execution time
    - circuit info
    - effective shots

## 4.3 `utils/helpers.py`

### `set_seed(seed)`

Sets seeds for:

- Python `random`
- NumPy
- torch (if available)

Also sets deterministic cuDNN flags when CUDA is active.

### `get_device_info()`

Returns:

- CPU thread count
- CUDA availability
- GPU details when available
- Windows fallback GPU detection through `wmic` when CUDA is absent

## 5) Charts and Analytical Outputs

In dashboard and benchmark reports, the following analyses are shown:

- Execution Time vs `N` (log-x)
- Throughput vs `N` (log-x)
- Resource efficiency chart:
  - CPU/GPU memory MB on one axis
  - QPU qubit count on secondary axis
- Speedup table vs CPU:
  - `speedup = cpu_time / platform_time`
- Empirical time exponent:
  - slope of `log(time)` vs `log(N)`

## 6) Complexity Interpretation

Expected behavior:

- CPU RNG: `O(N)`
- GPU RNG: approximately `O(N/P)` where `P` is effective parallelism
- QPU resource-width: qubits scale approximately with `log2(N)` in `logn` mode

Important interpretation note:

- MB and qubits are **not the same unit**.
- The repository compares architecture-appropriate resource indicators.

## 7) Dependency Behavior and Failure Modes

Required for full comparison:

- CPU baseline: `numpy` (plus `psutil` for memory metrics)
- GPU path: `torch` (+ CUDA for real GPU path)
- QPU path: `qiskit`, `qiskit-aer`
- Dashboard: `streamlit`, `plotly`, `pandas`

Typical errors:

- `No module named 'torch'` -> GPU path unavailable or fallback behavior
- `No module named 'qiskit'` -> QPU path unavailable
- `No module named 'psutil'` -> memory metrics may be limited in wrappers

## 8) Generated Artifact Paths

- Dashboard save:
  - `results/reports/focus_rng_dashboard_<timestamp>/`

- Batch benchmark:
  - `results/reports/focus_rng_<timestamp>/`

Typical files:

- `raw_runs.json`
- `results.csv`
- `summary.json` or `summary.csv`
- `report.md`
- plots

## 9) Design Decisions

1. Keep one unified wrapper (`RNGAlgorithm`) for fair cross-platform calling.
2. Keep both UI and CLI modes:
   - UI for exploration
   - CLI for repeatable scripted benchmark/reporting
3. Use batched simulator execution in quantum RNG for better runtime.
4. Keep fallback/error reporting explicit for missing dependencies.

## 10) Known Limitations

- QPU results are simulator-backed unless explicit IBM backend integration is used at runtime.
- Cross-architecture resource metrics are conceptually compared, not unit-equivalent.
- GPU benefits strongly depend on environment, driver, and CUDA availability.

## 11) Quick Command Reference

Dashboard:

```bash
streamlit run app.py
```

Batch benchmark:

```bash
python focus_rng_benchmark.py --counts 100,1000,5000,10000 --qubit-mode logn --max-qubits 10 --shots 1024
```

Minimal CLI run:

```bash
python main.py --count 1000 --qubits 8 --shots 1024 --seed 42
```
