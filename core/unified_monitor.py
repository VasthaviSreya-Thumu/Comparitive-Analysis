"""
Unified Monitor for Cross-Platform Search
Tracks memory, time, and performance metrics across CPU, GPU, and QPU
"""

import time
import psutil
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np


class UnifiedMonitor:
    """
    Monitor for cross-platform search experiments
    Tracks:
    - Execution time
    - Memory usage (System & GPU)
    - Algorithm performance
    """
    
    def __init__(self, logs_dir: Path = None):
        """
        Initialize monitor
        
        Args:
            logs_dir: Directory to save logs (optional)
        """
        self.process = psutil.Process(os.getpid())
        self.logs_dir = logs_dir
        if self.logs_dir:
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            
        self.metrics_history = []
    
    def get_system_memory(self) -> float:
        """Get current system memory usage in MB"""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def get_gpu_memory(self) -> float:
        """Get current GPU memory usage in MB"""
        try:
            import torch
            if torch.cuda.is_available():
                return torch.cuda.memory_allocated() / (1024 * 1024)
        except ImportError:
            pass
        return 0.0
    
    def log_experiment(self, platform: str, algorithm_name: str, 
                      database_size: int, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log experiment results
        
        Args:
            platform: 'CPU', 'GPU', or 'QPU'
            algorithm_name: Name of algorithm
            database_size: Size of search space
            results: Results dictionary from algorithm
            
        Returns:
            Combined metrics dictionary
        """
        timestamp = datetime.now().isoformat()
        
        # Base metrics
        metrics = {
            'timestamp': timestamp,
            'platform': platform,
            'algorithm': algorithm_name,
            'database_size': database_size,
            'found': results.get('found', False),
            'execution_time': results.get('search_time', 0.0),
            'memory_mb': results.get('peak_memory_mb', 0.0),
        }
        
        # Platform-specific metrics
        if platform == 'CPU':
            metrics['iterations'] = results.get('iterations', 0)
            metrics['items_per_second'] = results.get('items_per_second', 0)
            
        elif platform == 'GPU':
            metrics['items_per_second'] = results.get('items_per_second', 0)
            metrics['speedup_vs_cpu'] = results.get('speedup_vs_cpu', 0.0)
            
        elif platform == 'QPU':
            metrics['qubits'] = results.get('num_qubits', 0)
            metrics['circuit_depth'] = results.get('circuit_depth', 0)
            metrics['grover_iterations'] = results.get('grover_iterations', 0)
            metrics['success_probability'] = results.get('success_probability', 0.0)
            metrics['quantum_speedup'] = results.get('quantum_speedup_factor', 0.0)
        
        # Save info to history
        self.metrics_history.append(metrics)
        
        # Save to file if configured
        if self.logs_dir:
            self.save_metrics()
            
        return metrics
    
    def save_metrics(self):
        """Save all metrics to file"""
        if not self.logs_dir:
            return
            
        filename = f"search_metrics_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = self.logs_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)
            
    def compare_platforms(self, results_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare results across platforms
        
        Args:
            results_dict: Dictionary with keys 'CPU', 'GPU', 'QPU'
            
        Returns:
            Comparison metrics
        """
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'database_size': results_dict.get('database_info', {}).get('size', 0),
            'speedups': {},
            'memory_ratios': {}
        }
        
        platforms = results_dict.get('platforms', {})
        
        # Get baseline (CPU)
        cpu_time = platforms.get('CPU', {}).get('search_time', 0)
        cpu_mem = platforms.get('CPU', {}).get('peak_memory_mb', 0)
        
        if cpu_time > 0:
            for platform, data in platforms.items():
                if platform != 'CPU':
                    time_val = data.get('search_time', 0)
                    if time_val > 0:
                        speedup = cpu_time / time_val
                        comparison['speedups'][platform] = speedup
                        
        if cpu_mem > 0:
            for platform, data in platforms.items():
                if platform != 'CPU':
                    mem_val = data.get('peak_memory_mb', 0)
                    if mem_val > 0:
                        ratio = mem_val / cpu_mem
                        comparison['memory_ratios'][platform] = ratio
                        
        return comparison
