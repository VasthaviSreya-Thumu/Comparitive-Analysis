# Traceability Matrix: Repository Components to Manuscript Sections

This matrix maps meaningful repository files/modules/artifacts to manuscript sections to satisfy full-coverage traceability.

| Repository File / Artifact | Type | Evidence Used In Manuscript | Mapped Section(s) |
| --- | --- | --- | --- |
| `README.md` | Project spec / usage | Problem statement, run modes, dependency assumptions | Introduction, Reproducibility |
| `docs/DETAILED_DOCUMENTATION.md` | Technical documentation | Architecture and flow narrative, expected complexity framing | System Architecture, Methodology |
| `docs/VIVA_PREP_QA.md` | QA/defense notes | Clarifies intended scope and known constraints | Introduction, Limitations |
| `app.py` | Streamlit app | Interactive pipeline, metrics/plots, fallback visualization path | System Architecture, Implementation |
| `focus_rng_benchmark.py` | Batch benchmark engine | Core experimental protocol, warmup/repeats/CI, CSV/JSON/MD artifact export | Methodology, Experimental Setup, Results |
| `algorithms/rng_algorithm.py` | Cross-platform execution wrapper | CPU/GPU/QPU dispatch logic, fallback tagging, schema fields | Methodology, Implementation Details |
| `quantum/quantum_rng.py` | Quantum backend module | Circuit generation, simulator/hardware tagging, execution strategy | Methodology, Limitations |
| `utils/helpers.py` | Utility module | Seed control and hardware introspection logic | Reproducibility |
| `main.py` | CLI driver | One-shot execution path and environment printout | Artifact Evaluation |
| `run_dashboard.bat` | OS launcher | Windows run entrypoint | Reproducibility |
| `requirements.txt` | Dependency manifest | Package versions and required stack | Experimental Setup |
| `.env.example` | Runtime configuration template | IBM token placeholder for hardware path | Reproducibility, Limitations |
| `.gitignore` | Repository hygiene config | Documents intentionally excluded artifacts (venv/cache) | Reproducibility Appendix |
| `PROFILING_DESCRIPTION.md` | Legacy/partial doc | Contains historical energy/memory claims not fully supported by current code | Limitations, Threats to Validity |
| `algorithms/__init__.py` | Package export | Public API contract for algorithm module | Implementation Details |
| `quantum/__init__.py` | Package marker | Quantum module boundary | Implementation Details |
| `utils/__init__.py` | Package marker | Utility package boundary | Implementation Details |
| `results/__init__.py` | Package marker | Results package boundary | Implementation Details |
| `results/reports/paper_main/raw_runs.json` | Primary experimental artifact | Per-trial evidence for main study | Experimental Setup, Results |
| `results/reports/paper_main/results.csv` | Primary experimental artifact | Flattened per-platform/per-trial metrics | Results |
| `results/reports/paper_main/summary.json` | Primary experimental artifact | CI statistics, speedup table, fallback exclusion counts | Results |
| `results/reports/paper_main/report.md` | Generated report | Human-readable summary of primary run | Results |
| `results/reports/paper_main/execution_time_vs_count.png` | Generated figure | Runtime scaling chart | Results (Figure) |
| `results/reports/paper_main/resource_efficiency.png` | Generated figure | MB-vs-qubits resource chart | Results (Figure) |
| `results/reports/paper_ablation_include_fallback/*` | Ablation artifacts | Effect of including fallback GPU rows | Ablations/Error Analysis |
| `results/reports/paper_ablation_fixedq/*` | Ablation artifacts | Effect of fixed-vs-logn qubit policy | Ablations/Error Analysis |
| `results/reports/focus_rng_20260324_024923/*` | Historical negative-run artifacts | Missing `qiskit` failure evidence and earlier schema limitations | Negative Results, Limitations |
| `results/reports/phase1_smoke/*` | Method validation artifact | Sanity-check evidence for phase-1 methodology implementation | Reproducibility |
| `results/data/qpu_metrics.json` | Legacy data | Historical QPU telemetry-style metrics, treated as out-of-scope for current paper claims | Appendix: Legacy Artifacts |
| `results/data/search_comparison_N100_20260211_114900.json` | Legacy data | Prior search-problem artifact not aligned to RNG scope | Appendix: Legacy Artifacts |
| `results/data/search_comparison_N1000_20260211_120027.json` | Legacy data | Prior search-problem artifact not aligned to RNG scope | Appendix: Legacy Artifacts |
| `paper/tables/*.csv` | Derived manuscript tables | Final reported numbers for main and ablation analyses | Results, Ablations |
| `paper/tables/tables_quickview.md` | Table digest | Human-readable table snapshot for review | Results Appendix |
| `paper/figures/*.png` | Manuscript figures | Quantitative visual evidence for results and ablations | System Architecture, Results |
| `paper/figures/*.svg` | Manuscript figures | Vector pipeline diagram for architecture section | System Architecture |

## Explicitly Non-Meaningful Components (Excluded)

- `__pycache__/` bytecode files: build/runtime byproducts, no scientific evidence value.
- `.venv/` environment internals: dependency installation area, not a research artifact itself.
- `.git/` metadata: version-control internals.
- `.env`: local machine secret/config instance (not portable evidence artifact).
