# Focus RNG Architecture Comparison Report

- Generated: 2026-03-24T13:35:16
- Counts: [64, 128]
- Qubit mode: `logn`
- Shots: 1024
- Measured repeats per workload: 2
- Warmup runs per workload: 1
- Include fallback runs in analysis: False

## Problem Framing
Performance and resource efficiency comparison of Focus Algorithm RNG across CPU (O(N)), GPU (O(N/P)), and QPU with logarithmic qubit representation.

## Platform Summary

| Platform | Success/Analyzed/Total | Mean Time (s) | Std Time (s) | 95% CI Time (s) | Mean Throughput (/s) | Fallback Excluded | Empirical Time Exponent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CPU | 4/4/4 | 3.69505e-05 | 2.69302e-06 | [3.43113e-05, 3.95897e-05] | 2.63076e+06 | 0 | -0.0820145 |
| GPU | 0/0/4 | N/A | N/A | N/A | N/A | 4 | N/A |
| QPU | 4/4/4 | 0.128711 | 0.00311394 | [0.12566, 0.131763] | 751.338 | 0 | -0.0597705 |

## Speedup vs CPU

Speedups are computed from mean execution time across analyzed repeats per workload.

| Count (N) | GPU Speedup | QPU Speedup |
| --- | --- | --- |
| 64 | N/A | 0.000289248 |
| 128 | N/A | 0.000284822 |

## QPU Scaling Check

- Mean qubits: 6.5
- Mean log2(N): 6.5
- Mean ratio qubits/log2(N): 1

## Analysis Filtering

- Rows analyzed: 8 / 12
- Rows excluded as fallback: 4

## Artifacts

- `raw_runs.json`
- `results.csv`
- `summary.json`
- `report.md`
- `execution_time_vs_count.png`
- `resource_efficiency.png`
