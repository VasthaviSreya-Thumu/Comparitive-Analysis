# Viva Preparation: Focus RNG Repository

## 1) Core Understanding

### Q1. What is the exact problem statement solved by this repo?

It benchmarks RNG across CPU, GPU, and QPU and compares execution time with resource efficiency (MB for CPU/GPU and qubits for QPU), while analyzing scaling with workload size `N`.

### Q2. What is the primary app?

`app.py` (Streamlit Focus RNG dashboard).

### Q3. What are the entry points?

- `app.py`: interactive dashboard
- `focus_rng_benchmark.py`: batch report generator
- `main.py`: one-shot CLI comparison

### Q4. Is this a service or model training repository?

No. It is an algorithm benchmarking and analysis repository.

## 2) Architecture Questions

### Q5. How is code organized?

- `algorithms/rng_algorithm.py`: unified CPU/GPU/QPU wrapper
- `quantum/quantum_rng.py`: quantum RNG implementation
- `utils/helpers.py`: seed/device helpers
- entrypoints (`app.py`, `focus_rng_benchmark.py`, `main.py`)

### Q6. Why use a unified wrapper?

To ensure each architecture is called through a consistent interface and returns comparable metrics.

### Q7. What happens in a benchmark sweep?

For each workload size:

1. derive qubits
2. execute CPU, GPU, QPU RNG
3. collect timing/throughput/resource metrics
4. compute speedups and scaling
5. plot and/or export reports

## 3) Complexity and Scaling

### Q8. What complexity classes do you claim?

- CPU RNG: `O(N)`
- GPU RNG: approximately `O(N/P)`
- QPU memory-width requirement: approximately `O(log2(N))` qubits

### Q9. Are MB and qubits directly comparable?

No. They are architecture-specific resource indicators, not the same physical unit.

### Q10. What is empirical time exponent?

It is the slope of `log(time)` vs `log(N)` from observed runs, used to estimate practical scaling behavior.

## 4) RNG Implementation Questions

### Q11. How is CPU RNG implemented?

NumPy integer generation in `_run_cpu` (`np.random.randint`).

### Q12. How is GPU RNG implemented?

PyTorch `torch.randint` on CUDA tensors, with memory and timing capture.

### Q13. How is QPU RNG implemented?

Qiskit circuit with Hadamard on all qubits and measurement.

### Q14. What optimization did you apply in QPU RNG?

Simulator path is batched: one job with many shots instead of one job per random number.

### Q15. Why cap QPU count at 500000 in wrapper?

To prevent excessive simulation runtime during large sweeps.

## 5) Reliability and Dependencies

### Q16. What if CUDA is unavailable?

GPU path falls back to CPU-labeled behavior in RNG wrapper.

### Q17. What if Qiskit is missing?

QPU path fails with explicit import error.

### Q18. What if psutil is missing?

Some memory metrics become limited, but core RNG generation can still run.

### Q19. Why recommend Python 3.11?

It provides better compatibility for PyTorch/Qiskit/Streamlit dependencies.

## 6) Metrics and Reports

### Q20. What metrics do you report?

- execution time
- throughput (`numbers_per_second`)
- peak memory MB (CPU/GPU)
- qubit count (QPU)
- speedup vs CPU

### Q21. Where are results saved?

- dashboard save: `results/reports/focus_rng_dashboard_<timestamp>/`
- batch run: `results/reports/focus_rng_<timestamp>/`

### Q22. Which files are generated in batch mode?

- `raw_runs.json`
- `results.csv`
- `summary.json`
- `report.md`
- charts

## 7) Common Viva Follow-ups

### Q23. Why keep both dashboard and batch script?

Dashboard is ideal for interactive exploration; batch script is ideal for reproducible experimental reporting.

### Q24. How do you ensure reproducibility?

Seed control is centralized through `set_seed(...)` for Python, NumPy, and torch (if available).

### Q25. What is the main limitation of your QPU comparison?

Most runs are simulator-based, so they are not identical to real hardware behavior.

## 8) 30-Second Summary Answer

“This repository benchmarks one focused algorithmic task, RNG, across CPU, GPU, and QPU. It measures time, throughput, and architecture-appropriate resource usage, then analyzes scaling and speedup. The Streamlit dashboard is the primary interface, and a batch benchmark script generates reproducible reports for formal evaluation.”

