# Focus RNG Architecture Comparison Report

- Generated: 2026-03-24T13:50:18
- Counts: [64, 128, 256, 512, 1024]
- Qubit mode: `logn`
- Shots: 1024
- Measured repeats per workload: 5
- Warmup runs per workload: 2
- Include fallback runs in analysis: True

## Problem Framing
Performance and resource efficiency comparison of Focus Algorithm RNG across CPU (O(N)), GPU (O(N/P)), and QPU with logarithmic qubit representation.

## Platform Summary

| Platform | Success/Analyzed/Total | Mean Time (s) | Std Time (s) | 95% CI Time (s) | Mean Throughput (/s) | Fallback Excluded | Empirical Time Exponent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CPU | 25/25/25 | 4.08305e-05 | 3.97393e-06 | [3.92727e-05, 4.23883e-05] | 9.49395e+06 | 0 | 0.0304267 |
| GPU | 25/25/25 | 2.8809e-05 | 9.64668e-06 | [2.50275e-05, 3.25905e-05] | 1.29717e+07 | 0 | 0.174618 |
| QPU | 25/25/25 | 0.128385 | 0.00512042 | [0.126377, 0.130392] | 3106.56 | 0 | -0.00238548 |

## Speedup vs CPU

Speedups are computed from mean execution time across analyzed repeats per workload.

| Count (N) | GPU Speedup | QPU Speedup |
| --- | --- | --- |
| 64 | 1.72066 | 0.000311074 |
| 128 | 1.60203 | 0.000308665 |
| 256 | 1.41123 | 0.000309517 |
| 512 | 1.47889 | 0.000317697 |
| 1024 | 1.08651 | 0.000343549 |

## QPU Scaling Check

- Mean qubits: 8
- Mean log2(N): 8
- Mean ratio qubits/log2(N): 1

## Analysis Filtering

- Rows analyzed: 75 / 75
- Rows excluded as fallback: 0

## Artifacts

- `raw_runs.json`
- `results.csv`
- `summary.json`
- `report.md`
- `execution_time_vs_count.png`
- `resource_efficiency.png`
