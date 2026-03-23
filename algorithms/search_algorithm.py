"""
Unified Search Algorithm Interface
Provides a common interface for running the same search algorithm across CPU, GPU, and QPU
"""

import numpy as np
import time
from typing import Dict, Any, Optional, List


class SearchAlgorithm:
    """
    Unified search algorithm that can run on CPU, GPU, or QPU
    
    The search problem: Find a target item in an unsorted database
    - CPU: O(N) linear search
    - GPU: O(N/P) parallel search (P = number of cores)
    - QPU: O(√N) Grover's quantum search
    """
    
    def __init__(self, database_size: int, target_position: Optional[int] = None, seed: int = 42):
        """
        Initialize search algorithm
        """
        print("DEBUG: Initializing SearchAlgorithm (ASCII Fixed)")
        self.database_size = database_size
        self.seed = seed
        np.random.seed(seed)
        
        # Generate database and target
        self.database, self.target, self.target_position = self._generate_database(target_position)
        
    def _generate_database(self, target_position: Optional[int] = None):
        """
        Generate random database with a known target
        """
        # Create database of random integers
        database = np.random.randint(0, self.database_size * 10, size=self.database_size)
        
        # Set target position
        if target_position is None:
            target_position = np.random.randint(0, self.database_size)
        else:
            target_position = min(target_position, self.database_size - 1)
        
        # Mark target with unique value
        target = -1  # Unique marker
        database[target_position] = target
        
        return database, target, target_position
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the database"""
        return {
            'size': self.database_size,
            'target': self.target,
            'target_position': self.target_position,
            'memory_mb': self.database.nbytes / (1024 * 1024)
        }
    
    def search(self, platform: str, **kwargs) -> Dict[str, Any]:
        """
        Run search on specified platform
        """
        if platform.upper() == 'CPU':
            from algorithms.cpu_search import CPUSearch
            searcher = CPUSearch(self.database, self.target)
            return searcher.search(**kwargs)
            
        elif platform.upper() == 'GPU':
            from algorithms.gpu_search import GPUSearch
            searcher = GPUSearch(self.database, self.target)
            return searcher.search(**kwargs)
            
        elif platform.upper() == 'QPU':
            from algorithms.qpu_search import QPUSearch
            searcher = QPUSearch(self.database_size, self.target_position)
            return searcher.search(**kwargs)
            
        else:
            raise ValueError(f"Unknown platform: {platform}. Use 'CPU', 'GPU', or 'QPU'")
    
    def run_comparison(self, platforms: List[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Run search on multiple platforms and compare results
        """
        if platforms is None:
            platforms = ['CPU', 'GPU', 'QPU']
        
        results = {
            'database_info': self.get_database_info(),
            'platforms': {}
        }
        
        for platform in platforms:
            try:
                print(f"\nRunning {platform} search...")
                platform_result = self.search(platform, **kwargs)
                results['platforms'][platform] = platform_result
                
                # Verify correctness
                found_position = platform_result.get('found_position', -1)
                
                if found_position == self.target_position:
                    # Using ASCII [OK] instead of unicode checkmark
                    print(f"[OK] {platform} found target at correct position: {found_position}")
                else:
                    # Using ASCII [FAIL] instead of unicode ballot x
                    print(f"[FAIL] {platform} failed: found at {found_position}, expected {self.target_position}")
                    
            except Exception as e:
                # Using ASCII [FAIL] instead of unicode ballot x
                print(f"[FAIL] {platform} error: {str(e)}")
                results['platforms'][platform] = {
                    'error': str(e),
                    'success': False
                }
        
        return results
    
    def calculate_speedup(self, results: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate speedup factors relative to CPU
        """
        platforms = results.get('platforms', {})
        
        if 'CPU' not in platforms or 'search_time' not in platforms['CPU']:
            return {}
        
        cpu_time = platforms['CPU']['search_time']
        speedups = {}
        
        for platform, data in platforms.items():
            if platform != 'CPU' and 'search_time' in data:
                speedups[platform] = cpu_time / data['search_time']
        
        return speedups
