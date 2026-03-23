# Focus RNG Architecture Comparison Report

- Generated: 2026-03-24T02:49:23
- Counts: [100, 1000, 5000, 10000]
- Qubit mode: `logn`
- Shots: 1024

## Problem Framing
Performance and resource efficiency comparison of Focus Algorithm RNG across CPU (O(N)), GPU (O(N/P)), and QPU with logarithmic qubit representation.

## Platform Summary

| Platform | Success/Total | Mean Time (s) | Mean Throughput (/s) | Mean Peak Memory (MB) | Empirical Time Exponent |
| --- | --- | --- | --- | --- | --- |
| CPU | 4/4 | 4.93492e-05 | 7.89226e+07 | 0 | -0.0185364 |
| GPU | 4/4 | 3.79022e-05 | 8.72864e+07 | 0 | 0.140603 |
| QPU | 0/4 | N/A | N/A | N/A | N/A |

## Speedup vs CPU

| Count (N) | GPU Speedup | QPU Speedup |
| --- | --- | --- |
| 100 | 2.36033 | N/A |
| 1000 | 0.989687 | N/A |
| 5000 | 1.21471 | N/A |
| 10000 | 1.04707 | N/A |

## QPU Scaling Check

- No successful QPU runs to analyze.

## Failures

| Count | Platform | Error |
| --- | --- | --- |
| 100 | QPU | No module named 'qiskit' |
| 1000 | QPU | No module named 'qiskit' |
| 5000 | QPU | No module named 'qiskit' |
| 10000 | QPU | No module named 'qiskit' |

## Artifacts

- `raw_runs.json`
- `results.csv`
- `summary.json`
- `report.md`
- `execution_time_vs_count.png`
- `resource_efficiency.png`
