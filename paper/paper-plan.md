# Paper Plan (Phase 2)

## Target Venue Classes

1. Applied benchmarking / systems workshop (best immediate fit)
- Example classes: quantum-software workshops, HPC+QC integration workshops, reproducibility-focused tracks.
- Reason: repository contribution is empirical benchmarking framework + implementation artifact, not a new quantum algorithm proof.

2. Applied computing journal short paper / technical note (secondary fit)
- Reason: includes software artifact, reproducibility scripts, and architecture trade-off analysis.

3. Undergraduate/postgraduate thesis chapter format (strong fit)
- Reason: strong alignment with educational benchmarking objective and viva preparation materials.

## Proposed Title

**Focus RNG: A Reproducible CPU/GPU/QPU Benchmarking Framework for Runtime-Resource Trade-off Analysis**

## Detailed Outline

1. Abstract
- Problem statement and motivation.
- Architecture-aware benchmark design.
- Main empirical findings from repository artifacts.
- Limitations and scope.

2. Introduction
- Why cross-architecture RNG benchmarking matters.
- Practical mismatch between CPU/GPU memory metrics and QPU qubit metrics.
- Contributions list grounded in code/artifacts.

3. Related Work
- CPU/GPU PRNG benchmarking literature.
- QRNG and certified randomness literature.
- Gap: unified, reproducible CPU/GPU/QPU pipeline with explicit fallback handling.

4. Repository Contributions
- Unified execution interface.
- Benchmark harness with warmup/repeats/CI.
- Artifact generation and dashboard.
- Negative-result reporting and fallback filtering.

5. Methodology
- Task definition and complexity framing.
- Platform execution paths and backend taxonomy.
- Metrics and statistical treatment.
- Fairness caveats.

6. System Architecture
- End-to-end pipeline from parameters to artifacts.
- Data schema and output contracts.

7. Experimental Setup
- Environment and dependency versions.
- Workload grid, qubit policies, repeats/warmups.
- Experiment IDs and command lines.

8. Results
- Primary results (fallback-excluded analysis).
- Speedup and scaling interpretation.
- Resource trends.

9. Ablations and Error Analysis
- Fallback inclusion ablation.
- Qubit policy (logn vs fixed) ablation.
- Legacy dependency-failure run as negative result.

10. Limitations, Risks, and Scope Boundaries
- No true CUDA run in current environment.
- QPU results are simulator-only.
- Weak randomness-quality testing.
- Unit mismatch in MB vs qubits.

11. Reproducibility and Artifact Evaluation
- Exact commands, seeds, and output paths.
- How to rerun/verify tables and figures.

12. Conclusion and Future Work
- Conservative claims only.
- Required upgrades before stronger venue submission.

## File-to-Section Traceability

See [traceability-matrix.md](./traceability-matrix.md).
