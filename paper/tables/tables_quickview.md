# Manuscript Table Quickview

## Main Platform Summary

| platform | runs_total | runs_analyzed | runs_success | fallback_runs_excluded | mean_time_s | std_time_s | ci95_time_s_low | ci95_time_s_high | mean_throughput_numbers_per_s | mean_peak_memory_mb | empirical_time_exponent | backend_types |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CPU | 25 | 25 | 25 | 0 | 3.972952021285891e-05 | 6.669267969767997e-06 | 3.711516716870986e-05 | 4.234387325700797e-05 | 9697871.132786851 | 330.231875 | 0.058048787922858794 | cpu |
| GPU | 25 | 0 | 0 | 25 | None | None | None | None | None | None | None |  |
| QPU | 25 | 25 | 25 | 0 | 0.12995517476017995 | 0.009362689790795485 | 0.12628500036218812 | 0.13362534915817179 | 3074.089031264808 | 330.250625 | -0.01333831867232413 | simulator |

## Main Speedup vs CPU

| count | gpu_speedup_vs_cpu | qpu_speedup_vs_cpu |
| --- | --- | --- |
| 64 | None | 0.0002773522162196949 |
| 128 | None | 0.0002860102140538021 |
| 256 | None | 0.00030338523068028323 |
| 512 | None | 0.00033356076822057586 |
| 1024 | None | 0.0003289146603757065 |

## Fallback Inclusion Ablation

| count | gpu_speedup_excluding_fallback | gpu_speedup_including_fallback |
| --- | --- | --- |
| 64 | None | 1.7206567438756246 |
| 128 | None | 1.6020329794176094 |
| 256 | None | 1.4112298019206877 |
| 512 | None | 1.4788892482685114 |
| 1024 | None | 1.0865087812501457 |

## Qubit Mode Ablation

| qubit_mode | mean_qubits | mean_log2_count | mean_qubits_to_log2_count_ratio | qpu_mean_time_s | qpu_std_time_s |
| --- | --- | --- | --- | --- | --- |
| logn | 8.0 | 8.0 | 1.0 | 0.12995517476017995 | 0.009362689790795485 |
| fixed | 10.0 | 8.0 | 1.2912698412698413 | 0.1283927598001901 | 0.013514329674410401 |

## Legacy Failure Summary

| platform | runs_total | runs_success | runs_failed | mean_time_s |
| --- | --- | --- | --- | --- |
| CPU | 4 | 4 | 0 | 4.9349248911312316e-05 |
| GPU | 4 | 4 | 0 | 3.790224945987575e-05 |
| QPU | 4 | 0 | 4 | None |
