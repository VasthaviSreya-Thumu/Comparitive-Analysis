# Phase 1: Repository Census and Research Framing

## 1) Repository Structure Census

### Source code
- `app.py`: Streamlit dashboard entrypoint.
- `focus_rng_benchmark.py`: batch benchmark engine and report generator.
- `main.py`: one-shot CLI comparison.
- `algorithms/rng_algorithm.py`: unified CPU/GPU/QPU execution wrapper.
- `quantum/quantum_rng.py`: Qiskit-based RNG backend.
- `utils/helpers.py`: seed/device helpers.
- package markers: `algorithms/__init__.py`, `quantum/__init__.py`, `utils/__init__.py`, `results/__init__.py`.

### Configuration and execution
- `requirements.txt`
- `.env.example`
- `run_dashboard.bat`
- `.gitignore`

### Documentation
- `README.md`
- `docs/DETAILED_DOCUMENTATION.md`
- `docs/VIVA_PREP_QA.md`
- `PROFILING_DESCRIPTION.md` (legacy/partially stale with respect to current code).

### Experiment artifacts
- Primary study: `results/reports/paper_main/*`
- Ablation (fallback inclusion): `results/reports/paper_ablation_include_fallback/*`
- Ablation (fixed qubits): `results/reports/paper_ablation_fixedq/*`
- Historical negative run: `results/reports/focus_rng_20260324_024923/*`
- Phase-1 validation run: `results/reports/phase1_smoke/*`

### Legacy data artifacts (current scope mismatch)
- `results/data/search_comparison_N100_20260211_114900.json`
- `results/data/search_comparison_N1000_20260211_120027.json`
- `results/data/qpu_metrics.json`

### Not meaningful for scientific traceability
- `__pycache__/`
- `.venv/`
- `.git/`

## 2) Research Problem, Hypotheses, Claimed Contributions

### Problem statement inferred from repository
Benchmark runtime and resource behavior of RNG workloads across CPU, GPU, and QPU backends using architecture-specific resource indicators (MB for CPU/GPU, qubits for QPU).

### Working hypotheses (evidence-driven)
1. CPU runtime scales approximately linearly with workload size N.
2. GPU may outperform CPU only when true CUDA execution is available; CPU fallback can bias results.
3. QPU qubit requirements in `logn` mode follow approximately `ceil(log2(N))` by construction.
4. Simulator-based QPU execution incurs higher runtime than CPU for tested N in this environment.

### Claimed contributions supported by code
1. Unified multi-backend RNG interface (`RNGAlgorithm`).
2. Reproducible benchmark pipeline with warmup/repeats and confidence intervals (`focus_rng_benchmark.py`).
3. Explicit backend provenance (`backend_type`, `backend_name`) and fallback filtering.
4. Artifact export pipeline (raw JSON, CSV, summary JSON, markdown report, plots).

## 3) Implementation Architecture and Pipeline

1. Parse workload + qubit policy.
2. Optionally run warmups.
3. Execute repeated trials for CPU/GPU/QPU.
4. Flatten per-trial rows with backend/fallback metadata.
5. Compute summary statistics, CI, speedups, and scaling exponents.
6. Export report artifacts and figures.

See `paper/traceability-matrix.md` and `paper/figures/fig_pipeline_architecture.svg`.

## 4) Evidence Gaps and Methodological Risks

### G1: No true CUDA execution in current environment
- Evidence: `torch_cuda_available` is `False`; GPU rows in primary analysis are excluded as fallback.
- Impact: no validated CPU-vs-GPU hardware claim possible.

### G2: QPU results are simulator-only
- Evidence: backend type recorded as `simulator` (`aer_simulator`) in primary runs.
- Impact: cannot claim real-hardware QPU throughput.

### G3: Randomness quality tests are weak
- Evidence: only simple summary stats and an ad-hoc uniformity score in `quantum/quantum_rng.py`.
- Impact: no NIST/Diehard-level quality claim is supported.

### G4: Resource metrics are not physically commensurate
- Evidence: CPU/GPU use memory MB; QPU uses qubit count.
- Impact: cross-axis interpretation must remain qualitative/architecture-aware.

### G5: Legacy docs/data mismatch current scope
- Evidence: `PROFILING_DESCRIPTION.md` and `results/data/search_comparison_*` reflect older search/energy framing.
- Impact: these artifacts are treated as legacy appendix items, not primary evidence.

### G6: Environment constraints affect plotting cache location
- Evidence: matplotlib warning about unwritable default config path.
- Mitigation: set `MPLCONFIGDIR` to a writable path during reruns.

## 5) Explicit Unsupported Claims

- Real QPU hardware advantage over CPU/GPU: **Not supported by current repository evidence**.
- True GPU acceleration in tested environment: **Not supported by current repository evidence**.
- Cryptographic-quality randomness certification for generated outputs: **Not supported by current repository evidence**.
