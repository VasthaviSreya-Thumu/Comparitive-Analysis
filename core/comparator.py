"""
Experiment Comparator - Orchestrates CPU vs GPU vs QPU search experiments
"""

import json
from pathlib import Path
from datetime import datetime

from algorithms.search_algorithm import SearchAlgorithm
from core.unified_monitor import UnifiedMonitor
import config

class ExperimentComparator:
    """Run and compare CPU vs GPU vs QPU search experiments"""
    
    def __init__(self, dataset_name="Search_Database"):
        self.dataset_name = dataset_name
        self.results = []
        self.results_dir = config.RESULTS_DIR
        
    def run_search_comparison(self, database_size: int = 1000, target_position: int = None, monitor: bool = True):
        """
        Run search comparison across all platforms
        
        Args:
            database_size: Number of items in database
            target_position: Position of target (None = random)
            monitor: Whether to save metrics
            
        Returns:
            Dictionary with results from all platforms
        """
        # Create unified monitor
        monitor_dir = self.results_dir / 'logs' if monitor else None
        unified_monitor = UnifiedMonitor(monitor_dir) if monitor else None
        
        # Initialize search algorithm
        search = SearchAlgorithm(database_size, target_position)
        
        print(f"\nRunning Cross-Platform Search Comparison (N={database_size})...")
        
        # Run on all platforms
        # Note: QPU simulator can be slow for large N, so we might want to limit QPU for very large sizes
        # But for now we run all
        results = search.run_comparison(platforms=['CPU', 'GPU', 'QPU'], shots=1024)
        
        # Calculate comparison metrics
        speedups = search.calculate_speedup(results)
        
        # Log to monitor
        if unified_monitor:
            for platform, data in results['platforms'].items():
                if 'error' not in data:
                    unified_monitor.log_experiment(
                        platform=platform,
                        algorithm_name=data.get('algorithm', 'Unknown'),
                        database_size=database_size,
                        results=data
                    )
        
        # Add comparison analysis
        results['analysis'] = {
            'speedups': speedups,
            'theoretical_complexity': {
                'CPU': 'O(N)',
                'GPU': 'O(N/P)',
                'QPU': 'O(√N)'
            }
        }
        
        self.results.append(results)
        
        # Save individual result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"search_comparison_N{database_size}_{timestamp}.json"
        with open(self.results_dir / filename, 'w') as f:
            json.dump(results, f, indent=2)
            
        return results
        
    def run_batch_size_comparison(self, database_sizes: list):
        """
        Run search comparison across different database sizes
        """
        print(f"\n{'='*80}")
        print(f"Running Scale Comparison (Database Sizes: {database_sizes})")
        print(f"{'='*80}")
        
        all_results = []
        
        for size in database_sizes:
            result = self.run_search_comparison(database_size=size)
            all_results.append(result)
            
        return all_results
    
    def save_all_results(self, filename="all_search_results.json"):
        """Save all experiment results"""
        results_file = self.results_dir / filename
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nAll results saved to {results_file}")
        
    def get_results(self):
        """Get all experiment results"""
        return self.results
