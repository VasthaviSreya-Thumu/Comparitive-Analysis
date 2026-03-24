# Cover Letter Draft

Dear Editor / Program Committee,

Please find enclosed our manuscript:

**"Focus RNG: A Reproducible CPU/GPU/QPU Benchmarking Framework for Runtime-Resource Trade-off Analysis"**.

This submission presents an artifact-driven benchmarking framework that compares RNG execution across CPU, GPU, and QPU backends with explicit backend provenance and fallback handling. The core contribution is methodological reproducibility: the repository provides a unified execution interface, repeated-trial statistics with confidence intervals, exportable artifacts, and a complete traceability map linking code and outputs to manuscript claims.

Key strengths of the submission:
1. Explicit treatment of fallback confounds (for example, GPU CPU-fallback) and their effect on speedup interpretation.
2. End-to-end reproducibility package (`paper/`) including commands, environment snapshot, artifact evaluation protocol, and traceability matrix.
3. Transparent reporting of negative and constrained findings (for example, missing real CUDA path in the current environment and simulator-only QPU data).

Scope boundaries are clearly stated: the manuscript does not claim real-hardware quantum advantage or true GPU acceleration in environments where corresponding hardware execution is unavailable.

We believe this work fits venues valuing reproducible systems benchmarking, practical hybrid computing workflows, and artifact quality.

Sincerely,

[Author Name(s)]
