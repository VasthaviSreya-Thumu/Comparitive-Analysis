# Focus RNG Architecture Comparison Report

- Generated: 2026-03-24T13:50:34
- Counts: [64, 128, 256, 512, 1024]
- Qubit mode: `fixed`
- Shots: 1024
- Measured repeats per workload: 5
- Warmup runs per workload: 2
- Include fallback runs in analysis: False

## Problem Framing
Performance and resource efficiency comparison of Focus Algorithm RNG across CPU (O(N)), GPU (O(N/P)), and QPU with logarithmic qubit representation.

## Platform Summary

| Platform | Success/Analyzed/Total | Mean Time (s) | Std Time (s) | 95% CI Time (s) | Mean Throughput (/s) | Fallback Excluded | Empirical Time Exponent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CPU | 25/25/25 | 3.92724e-05 | 3.52417e-06 | [3.78909e-05, 4.06538e-05] | 9.68806e+06 | 0 | 0.0486931 |
| GPU | 0/0/25 | N/A | N/A | N/A | N/A | 25 | N/A |
| QPU | 25/25/25 | 0.128393 | 0.0135143 | [0.123095, 0.13369] | 3189.28 | 0 | -0.0319629 |

## Speedup vs CPU

Speedups are computed from mean execution time across analyzed repeats per workload.

| Count (N) | GPU Speedup | QPU Speedup |
| --- | --- | --- |
| 64 | N/A | 0.000293003 |
| 128 | N/A | 0.00026697 |
| 256 | N/A | 0.000304465 |
| 512 | N/A | 0.000313639 |
| 1024 | N/A | 0.00035751 |

## QPU Scaling Check

- Mean qubits: 10
- Mean log2(N): 8
- Mean ratio qubits/log2(N): 1.29127

## Analysis Filtering

- Rows analyzed: 50 / 75
- Rows excluded as fallback: 25

## Artifacts

- `raw_runs.json`
- `results.csv`
- `summary.json`
- `report.md`
- `execution_time_vs_count.png`
- `resource_efficiency.png`
