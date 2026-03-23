"""
GPU Parallel Search Implementation
Parallel search using PyTorch CUDA
"""

import numpy as np
import torch
import time
from typing import Dict, Any, Optional


class GPUSearch:
    """
    GPU-based parallel search implementation
    Complexity: O(N/P) where P = number of parallel threads
    """
    
    def __init__(self, database: np.ndarray, target: Any):
        """
        Initialize GPU search
        
        Args:
            database: Array to search
            target: Value to find
        """
        self.database = database
        self.target = target
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        if not torch.cuda.is_available():
            print("Warning: CUDA not available, falling back to CPU")
    
    def search(self, chunk_size: int = 10000, **kwargs) -> Dict[str, Any]:
        """
        Perform parallel search on GPU
        
        Args:
            chunk_size: Size of chunks to process in parallel
            **kwargs: Additional parameters (ignored)
            
        Returns:
            Dictionary with search results and metrics
        """
        start_time = time.time()
        
        # Track GPU memory if available
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            start_memory = torch.cuda.memory_allocated() / (1024 * 1024)  # MB
        else:
            start_memory = 0
        
        # Convert to torch tensor
        database_tensor = torch.from_numpy(self.database).to(self.device)
        target_tensor = torch.tensor(self.target, device=self.device)
        
        # Parallel search using vectorized comparison
        matches = (database_tensor == target_tensor)
        found_indices = torch.where(matches)[0]
        
        if len(found_indices) > 0:
            found_position = found_indices[0].item()
            found = True
        else:
            found_position = -1
            found = False
        
        # Synchronize GPU
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        
        end_time = time.time()
        
        # GPU memory metrics
        if torch.cuda.is_available():
            end_memory = torch.cuda.memory_allocated() / (1024 * 1024)
            peak_memory = torch.cuda.max_memory_allocated() / (1024 * 1024)
        else:
            end_memory = 0
            peak_memory = 0
        
        search_time = end_time - start_time
        
        return {
            'platform': 'GPU' if torch.cuda.is_available() else 'CPU (fallback)',
            'algorithm': 'Parallel Search',
            'complexity': 'O(N/P)',
            'found': found,
            'found_position': found_position,
            'search_time': search_time,
            'start_memory_mb': start_memory,
            'end_memory_mb': end_memory,
            'peak_memory_mb': peak_memory,
            'memory_used_mb': end_memory - start_memory,
            'database_size': len(self.database),
            'items_per_second': len(self.database) / search_time if search_time > 0 else 0,
            'cuda_available': torch.cuda.is_available(),
            'device': str(self.device),
            'success': found
        }
    
    def search_chunked(self, chunk_size: int = 500000) -> Dict[str, Any]:
        """
        Perform chunked parallel search (useful for very large databases)
        
        Args:
            chunk_size: Size of each chunk to process
            
        Returns:
            Dictionary with search results and metrics
        """
        start_time = time.time()
        
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            start_memory = torch.cuda.memory_allocated() / (1024 * 1024)
        else:
            start_memory = 0
        
        found_position = -1
        chunks_processed = 0
        
        # Process in chunks
        for i in range(0, len(self.database), chunk_size):
            chunk = self.database[i:i + chunk_size]
            chunk_tensor = torch.from_numpy(chunk).to(self.device)
            target_tensor = torch.tensor(self.target, device=self.device)
            
            # Search in chunk
            matches = (chunk_tensor == target_tensor)
            found_indices = torch.where(matches)[0]
            
            if len(found_indices) > 0:
                found_position = i + found_indices[0].item()
                break
            
            chunks_processed += 1
        
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        
        end_time = time.time()
        
        if torch.cuda.is_available():
            end_memory = torch.cuda.memory_allocated() / (1024 * 1024)
            peak_memory = torch.cuda.max_memory_allocated() / (1024 * 1024)
        else:
            end_memory = 0
            peak_memory = 0
        
        search_time = end_time - start_time
        
        return {
            'platform': 'GPU' if torch.cuda.is_available() else 'CPU (fallback)',
            'algorithm': 'Chunked Parallel Search',
            'complexity': 'O(N/P)',
            'found': found_position != -1,
            'found_position': found_position,
            'search_time': search_time,
            'chunks_processed': chunks_processed,
            'chunk_size': chunk_size,
            'start_memory_mb': start_memory,
            'end_memory_mb': end_memory,
            'peak_memory_mb': peak_memory,
            'memory_used_mb': end_memory - start_memory,
            'database_size': len(self.database),
            'items_per_second': len(self.database) / search_time if search_time > 0 else 0,
            'cuda_available': torch.cuda.is_available(),
            'device': str(self.device),
            'success': found_position != -1
        }
