# Focus RNG Architecture Comparison Report

- Generated: 2026-03-24T13:50:03
- Counts: [64, 128, 256, 512, 1024]
- Qubit mode: `logn`
- Shots: 1024
- Measured repeats per workload: 5
- Warmup runs per workload: 2
- Include fallback runs in analysis: False

## Problem Framing
Performance and resource efficiency comparison of Focus Algorithm RNG across CPU (O(N)), GPU (O(N/P)), and QPU with logarithmic qubit representation.

## Platform Summary

| Platform | Success/Analyzed/Total | Mean Time (s) | Std Time (s) | 95% CI Time (s) | Mean Throughput (/s) | Fallback Excluded | Empirical Time Exponent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CPU | 25/25/25 | 3.97295e-05 | 6.66927e-06 | [3.71152e-05, 4.23439e-05] | 9.69787e+06 | 0 | 0.0580488 |
| GPU | 0/0/25 | N/A | N/A | N/A | N/A | 25 | N/A |
| QPU | 25/25/25 | 0.129955 | 0.00936269 | [0.126285, 0.133625] | 3074.09 | 0 | -0.0133383 |

## Speedup vs CPU

Speedups are computed from mean execution time across analyzed repeats per workload.

| Count (N) | GPU Speedup | QPU Speedup |
| --- | --- | --- |
| 64 | N/A | 0.000277352 |
| 128 | N/A | 0.00028601 |
| 256 | N/A | 0.000303385 |
| 512 | N/A | 0.000333561 |
| 1024 | N/A | 0.000328915 |

## QPU Scaling Check

- Mean qubits: 8
- Mean log2(N): 8
- Mean ratio qubits/log2(N): 1

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
