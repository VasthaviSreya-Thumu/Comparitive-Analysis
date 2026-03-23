"""
CPU Linear Search Implementation
Classic O(N) sequential search algorithm
"""

import numpy as np
import time
import psutil
import os
from typing import Dict, Any


class CPUSearch:
    """
    CPU-based linear search implementation
    Complexity: O(N) - checks each element sequentially
    """
    
    def __init__(self, database: np.ndarray, target: Any):
        """
        Initialize CPU search
        
        Args:
            database: Array to search
            target: Value to find
        """
        self.database = database
        self.target = target
        self.process = psutil.Process(os.getpid())
    
    def search(self, monitor_memory: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Perform linear search on CPU
        
        Args:
            monitor_memory: Whether to track memory usage
            **kwargs: Additional parameters (ignored)
            
        Returns:
            Dictionary with search results and metrics
        """
        # Initialize metrics
        start_time = time.perf_counter() # Use perf_counter for high precision
        start_memory = self.process.memory_info().rss / (1024 * 1024)  # MB
        peak_memory = start_memory
        
        iterations = 0
        found_position = -1
        
        # Linear search
        for i in range(len(self.database)):
            iterations += 1
            
            if self.database[i] == self.target:
                found_position = i
                break
            
            # Monitor memory every 10000 iterations
            if monitor_memory and iterations % 10000 == 0:
                current_memory = self.process.memory_info().rss / (1024 * 1024)
                peak_memory = max(peak_memory, current_memory)
        
        # Final metrics
        end_time = time.perf_counter()
        end_memory = self.process.memory_info().rss / (1024 * 1024)
        
        search_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        return {
            'platform': 'CPU',
            'algorithm': 'Linear Search',
            'complexity': 'O(N)',
            'found': found_position != -1,
            'found_position': found_position,
            'iterations': iterations,
            'search_time': search_time,
            'start_memory_mb': start_memory,
            'end_memory_mb': end_memory,
            'peak_memory_mb': peak_memory,
            'memory_used_mb': memory_used,
            'database_size': len(self.database),
            'items_per_second': len(self.database) / search_time if search_time > 0 else 0,
            'success': found_position != -1
        }
    
    def search_with_monitoring(self, sample_interval: int = 1000) -> Dict[str, Any]:
        """
        Perform search with detailed memory monitoring
        
        Args:
            sample_interval: How often to sample memory (in iterations)
            
        Returns:
            Dictionary with detailed metrics including memory timeline
        """
        start_time = time.perf_counter()
        start_memory = self.process.memory_info().rss / (1024 * 1024)
        
        iterations = 0
        found_position = -1
        memory_samples = []
        time_samples = []
        
        # Linear search with monitoring
        for i in range(len(self.database)):
            iterations += 1
            
            if self.database[i] == self.target:
                found_position = i
                break
            
            # Sample memory
            if iterations % sample_interval == 0:
                current_time = time.perf_counter() - start_time
                current_memory = self.process.memory_info().rss / (1024 * 1024)
                memory_samples.append(current_memory)
                time_samples.append(current_time)
        
        end_time = time.perf_counter()
        end_memory = self.process.memory_info().rss / (1024 * 1024)
        
        return {
            'platform': 'CPU',
            'algorithm': 'Linear Search',
            'complexity': 'O(N)',
            'found': found_position != -1,
            'found_position': found_position,
            'iterations': iterations,
            'search_time': end_time - start_time,
            'start_memory_mb': start_memory,
            'end_memory_mb': end_memory,
            'peak_memory_mb': max(memory_samples) if memory_samples else end_memory,
            'memory_used_mb': end_memory - start_memory,
            'database_size': len(self.database),
            'items_per_second': len(self.database) / (end_time - start_time),
            'memory_timeline': memory_samples,
            'time_timeline': time_samples,
            'success': found_position != -1
        }
