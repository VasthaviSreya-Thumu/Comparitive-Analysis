"""
Main Application - CPU vs GPU vs QPU Search Algorithm Comparison
"""

import argparse
import sys
import torch
from pathlib import Path
import config
from core.comparator import ExperimentComparator
from utils.helpers import get_device_info

def print_banner():
    """Print application banner"""
    print("\n" + "=" * 80)
    print(" " * 20 + "Cross-Platform Search Algorithm Comparison")
    print(" " * 25 + "CPU vs GPU vs QPU Performance Study")
    print("=" * 80)
    print()

def check_environment():
    """Check and display environment information"""
    print("Environment Check:")
    print("-" * 80)
    
    device_info = get_device_info()
    print(f"CPU Threads: {device_info.get('cpu_count', 'Unknown')}")
    print(f"CUDA Available: {device_info.get('cuda_available', False)}")
    
    if device_info.get('cuda_available'):
        print(f"GPU Count: {device_info.get('gpu_count', 0)}")
        print(f"GPU Name: {device_info.get('gpu_name', 'Unknown')}")
    else:
        print("! Warning: CUDA not available. GPU experiments will use CPU fallback or simulation.")
    
    print("-" * 80)
    print()

def run_experiment(algorithm, **kwargs):
    """Run experiment for specified algorithm"""
    print(f"\n> Running {algorithm.upper()} Comparison...")
    
    results = {}
    
    if algorithm == 'search':
        from algorithms.search_algorithm import SearchAlgorithm
        
        size = kwargs.get('size', 1000)
        target = kwargs.get('target', None)
        
        runner = SearchAlgorithm(database_size=size, target_position=target)
        results = runner.run_comparison()
        
        # Visualize
        output_chart = config.CHARTS_DIR / f'search_comparison_N{size}.png'
        # create_cpu_gpu_qpu_comparison(results, str(output_chart)) # Needs update for generic results
        
    elif algorithm == 'rng':
        from algorithms.rng_algorithm import RNGAlgorithm
        
        count = kwargs.get('count', 1000)
        runner = RNGAlgorithm(count=count)
        results = runner.run_comparison()
        
    elif algorithm == 'game':
        from algorithms.game_algorithm import GameAlgorithm
        
        games = kwargs.get('games', 10)
        runner = GameAlgorithm(num_games=games)
        results = runner.run_comparison()
        
    else:
        print(f"Unknown algorithm: {algorithm}")
        return

    # Print Summary
    print("\nResults Summary:")
    print("-" * 60)
    platforms = results.get('platforms', {})
    
    for platform, data in platforms.items():
        success = "[OK]" if data.get('success') else "[FAIL]"
        print(f"{success} {platform}: {data.get('algorithm', 'Unknown')}")
        
        if 'search_time' in data:
            print(f"    Time: {data['search_time']:.6f}s")
        elif 'generation_time' in data:
            print(f"    Time: {data['generation_time']:.6f}s ({data.get('numbers_per_second', 0):.0f} nums/s)")
        elif 'time_seconds' in data:
            print(f"    Time: {data['time_seconds']:.6f}s ({data.get('games_per_second', 0):.2f} games/s)")
            
        if 'error' in data:
            print(f"    Error: {data['error']}")
            
    print("-" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='CPU vs GPU vs QPU Search Comparison',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--algorithm', type=str, choices=['search', 'rng', 'game'], default='search',
                      help='Algorithm to compare (default: search)')
    
    # Search args
    parser.add_argument('--size', type=int, default=1000, help='Database size (Search) or Count (RNG)')
    parser.add_argument('--target', type=int, help='Target position (Search)')
    
    # Game args
    parser.add_argument('--games', type=int, default=10, help='Number of games (Game)')
    
    # Generic flags
    parser.add_argument('--test', action='store_true', help='Run simple test')
    
    args = parser.parse_args()
    
    print_banner()
    check_environment()
    
    try:
        run_experiment(
            args.algorithm,
            size=args.size, # doubling as count for RNG
            count=args.size,
            target=args.target,
            games=args.games
        )
            
    except KeyboardInterrupt:
        print("\n! Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nX Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
