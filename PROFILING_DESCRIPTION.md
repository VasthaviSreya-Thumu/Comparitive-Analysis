# Memory and Energy Profiling: Detailed Description

This document provides a technical overview of how memory and energy metrics are tracked, calculated, and compared across CPU, GPU, and QPU platforms in this project.

## 💾 1. Memory Profiling

Memory profiling focuses on the peak and average space required to store datasets and execute search algorithms.

### **CPU (System RAM)**
- **Method**: Utilizes the `psutil` library in Python.
- **Metric**: **Resident Set Size (RSS)** - the non-swapped physical memory a process has used.
- **Implementation**: 
  ```python
  self.process = psutil.Process(os.getpid())
  memory_mb = self.process.memory_info().rss / (1024 * 1024)
  ```
- **Context**: tracks how the OS allocates memory for the search database and the overhead of linear iteration.

### **GPU (VRAM)**
- **Method**: Uses the `torch.cuda` interface.
- **Metric**: **Allocated Memory** - the current memory allocated by PyTorch for tensors on the device.
- **Implementation**:
  ```python
  memory_mb = torch.cuda.memory_allocated() / (1024 * 1024)
  ```
- **Context**: Measures the footprint of parallelized tensors. GPU memory is often more limited but faster than RAM.

### **QPU (Qubits)**
- **Method**: Algorithmic calculation based on database size ($N$).
- **Metric**: **Qubit Count** ($n = \lceil \log_2 N \rceil$).
- **Context**: In quantum computing, "memory" is represented by the number of qubits required to encode the search space. A database of 1,000 items requires approximately 10 qubits.

---

## ⚡ 2. Energy Profiling

Energy profiling measures the electrical cost of computation, typically expressed in **Joules** ($J$).

### **The Formula**
$$Energy (Joules) = Power (Watts) \times Time (Seconds)$$

### **CPU Energy Estimation**
Since direct hardware sensors vary across systems, we estimate energy using:
1. **Utilization**: Measured via `psutil.cpu_percent()`.
2. **TDP (Thermal Design Power)**: The maximum power the CPU is designed to dissipate.
3. **Calculation**: `(Current_Utilization / 100) * TDP * Runtime`.

### **GPU Energy Tracking**
- **Sensing**: Polled via the **NVIDIA Management Library (NVML)** or the `nvidia-smi` utility.
- **Accuracy**: Provides real-time "Board Power Draw" in Watts.
- **Optimization**: This project highlights how **FP16 (Mixed Precision)** reduces energy by shortening training time and reducing the switching activity in the GPU cores.

### **QPU Energy Efficiency**
Quantum energy profiling is unique:
- **Overhead**: Most energy is consumed by the **dilution refrigerator** (cooling to millikelvin) and the control electronics, regardless of the algorithm's complexity.
- **Scalability**: For massive datasets, Grover's $O(\sqrt{N})$ complexity potentially consumes less total energy than classical $O(N)$ despite high cooling overhead, as the runtime is drastically shorter.

---

## 📊 3. Comparative Summary

| Platform | Memory Metric | Primary Energy Driver | Scaling Law |
| :--- | :--- | :--- | :--- |
| **CPU** | RAM (MB) | Frequency & Core Count | $O(N)$ |
| **GPU** | VRAM (MB) | TFLOPS & Memory Bandwidth | $O(N/P)$ |
| **QPU** | Qubits | Cryogenic Cooling | $O(\sqrt{N})$ |
