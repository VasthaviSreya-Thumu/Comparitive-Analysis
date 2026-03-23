"""
Unified Random Number Generation (RNG) Algorithm Interface
Compares CPU (Pseudo-RNG), GPU (Parallel Pseudo-RNG), and QPU (True Quantum RNG)
"""

import numpy as np
import time
from typing import Dict, Any, Optional, List

try:
    import torch
except ImportError:  # pragma: no cover - runtime-dependent optional dependency
    torch = None

class RNGAlgorithm:
    """
    Unified RNG algorithm that can run on CPU, GPU, or QPU
    
    The problem: Generate N random numbers
    - CPU: Sequential generation (Mersenne Twister) - O(N)
    - GPU: Parallel generation (XORWOW/Philox) - O(N/P)
    - QPU: True random generation (Superposition collapse) - O(N) but true randomness
    """
    
    def __init__(self, count: int = 1000, num_qubits: int = 5, seed: int = 42):
        """
        Initialize RNG algorithm
        
        Args:
            count: Number of random numbers to generate
            num_qubits: Number of qubits for QPU (limit range to 0..2^n-1)
            seed: Random seed for reproducibility (CPU/GPU only)
        """
        self.count = count
        self.num_qubits = num_qubits
        self.seed = seed
        self.max_value = 2 ** num_qubits - 1
        
    def get_info(self) -> Dict[str, Any]:
        """Get information about the task"""
        return {
            'count': self.count,
            'range': f"[0, {self.max_value}]",
            'num_qubits': self.num_qubits
        }
    
    def run(self, platform: str, **kwargs) -> Dict[str, Any]:
        """
        Run RNG on specified platform
        """
        if platform.upper() == 'CPU':
            return self._run_cpu(**kwargs)
        elif platform.upper() == 'GPU':
            return self._run_gpu(**kwargs)
        elif platform.upper() == 'QPU':
            return self._run_qpu(**kwargs)
        else:
            raise ValueError(f"Unknown platform: {platform}. Use 'CPU', 'GPU', or 'QPU'")
            
    def _run_cpu(self, **kwargs) -> Dict[str, Any]:
        """Run on CPU using numpy"""
        process = None
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
        except ImportError:
            process = None

        start_mem = process.memory_info().rss / (1024 * 1024) if process else 0.0
        
        np.random.seed(self.seed)
        
        start_time = time.perf_counter()
        # Generate random integers
        numbers = np.random.randint(0, self.max_value + 1, size=self.count)
        end_time = time.perf_counter()
        
        end_mem = process.memory_info().rss / (1024 * 1024) if process else 0.0
        peak_mem = end_mem # simplify for now
        
        generation_time = end_time - start_time
        
        return {
            'platform': 'CPU',
            'algorithm': 'Pseudo-RNG (Mersenne Twister)',
            'count': self.count,
            'numbers': numbers.tolist()[:20], # Only return first 20 for display
            'generation_time': generation_time,
            'numbers_per_second': self.count / generation_time if generation_time > 0 else 0,
            'peak_memory_mb': peak_mem,
            'memory_used_mb': max(0, end_mem - start_mem),
            'success': True
        }
        
    def _run_gpu(self, **kwargs) -> Dict[str, Any]:
        """Run on GPU using PyTorch"""
        if torch is None or not torch.cuda.is_available():
            # Fallback to CPU if no GPU
            cpu_result = self._run_cpu(**kwargs)
            cpu_result.update({
                'platform': 'GPU',
                'note': 'PyTorch/CUDA not available (CPU Fallback)',
                'algorithm': 'Parallel Pseudo-RNG (CPU Fallback)'
            })
            return cpu_result
            
        device = torch.device('cuda')
        torch.cuda.manual_seed(self.seed)
        
        start_time = time.perf_counter()
        
        # Generate on GPU
        torch.cuda.reset_peak_memory_stats()
        start_mem = torch.cuda.memory_allocated() / (1024 * 1024)
        
        numbers_tensor = torch.randint(0, self.max_value + 1, (self.count,), device=device)
        
        # Synchronize to measure actual time
        torch.cuda.synchronize()
        end_time = time.perf_counter()
        
        end_mem = torch.cuda.memory_allocated() / (1024 * 1024)
        peak_mem = torch.cuda.max_memory_allocated() / (1024 * 1024)
        
        generation_time = end_time - start_time
        
        return {
            'platform': 'GPU',
            'algorithm': 'Parallel Pseudo-RNG',
            'count': self.count,
            'numbers': numbers_tensor.cpu().numpy().tolist()[:20],
            'generation_time': generation_time,
            'numbers_per_second': self.count / generation_time if generation_time > 0 else 0,
            'peak_memory_mb': peak_mem,
            'memory_used_mb': max(0, end_mem - start_mem),
            'success': True
        }
        
    def _run_qpu(self, shots: int = 1024, **kwargs) -> Dict[str, Any]:
        """Run on QPU using quantum_rng module"""
        process = None
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
        except ImportError:
            process = None
        start_mem = process.memory_info().rss / (1024 * 1024) if process else 0.0

        from quantum.quantum_rng import run_quantum_rng
        
        actual_count = min(self.count, 500000) # Soft cap for simulation speed
        
        try:
            result = run_quantum_rng(
                num_qubits=self.num_qubits,
                count=actual_count,
                shots=shots
            )
            
            end_mem = process.memory_info().rss / (1024 * 1024) if process else 0.0
            
            return {
                'platform': 'QPU',
                'algorithm': 'True Quantum RNG',
                'count': result['count'],
                'numbers': result['numbers'][:20],
                'generation_time': result['execution_time'],
                'numbers_per_second': result['count'] / result['execution_time'] if result['execution_time'] > 0 else 0,
                'circuit_info': result['circuit_info'],
                'num_qubits': self.num_qubits, # Explicitly added for UI
                'peak_memory_mb': end_mem, 
                'memory_used_mb': max(0, end_mem - start_mem),
                'success': True
            }
        except Exception as e:
            return {
                'platform': 'QPU',
                'error': str(e),
                'success': False
            }

    def run_comparison(self, platforms: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Run on all platforms"""
        if platforms is None:
            platforms = ['CPU', 'GPU', 'QPU']
            
        results = {
            'info': self.get_info(),
            'platforms': {}
        }
        
        for platform in platforms:
            try:
                print(f"Running RNG on {platform}...")
                results['platforms'][platform] = self.run(platform, **kwargs)
            except Exception as e:
                print(f"Error on {platform}: {e}")
                results['platforms'][platform] = {'error': str(e), 'success': False}
                
        return results
