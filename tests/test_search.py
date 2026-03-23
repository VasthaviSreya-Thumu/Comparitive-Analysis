"""
Test script for cross-platform search algorithms
"""

from algorithms.search_algorithm import SearchAlgorithm
import json

def test_small_search():
    """Test with small database"""
    print("="*80)
    print("Testing Cross-Platform Search - Small Database (1000 items)")
    print("="*80)
    
    # Create search problem
    search = SearchAlgorithm(database_size=1000, target_position=500)
    
    print(f"\nDatabase Info:")
    info = search.get_database_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Run comparison
    results = search.run_comparison(platforms=['CPU', 'GPU', 'QPU'], shots=1024)
    
    # Calculate speedups
    speedups = search.calculate_speedup(results)
    
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    
    for platform, data in results['platforms'].items():
        if 'error' in data:
            print(f"\n{platform}: ERROR - {data['error']}")
            continue
            
        print(f"\n{platform}:")
        print(f"  Algorithm: {data.get('algorithm', 'N/A')}")
        print(f"  Complexity: {data.get('complexity', 'N/A')}")
        print(f"  Found: {data.get('found', False)}")
        print(f"  Position: {data.get('found_position', -1)}")
        print(f"  Search Time: {data.get('search_time', 0):.4f}s")
        
        if platform in speedups:
            print(f"  Speedup vs CPU: {speedups[platform]:.2f}x")
        
        if 'iterations' in data:
            print(f"  Iterations: {data['iterations']}")
        if 'grover_iterations' in data:
            print(f"  Grover Iterations: {data['grover_iterations']}")
        if 'success_probability' in data:
            print(f"  Success Probability: {data['success_probability']:.1%}")
    
    print("\n" + "="*80)
    
    return results

def test_medium_search():
    """Test with medium database"""
    print("\n\n" + "="*80)
    print("Testing Cross-Platform Search - Medium Database (100,000 items)")
    print("="*80)
    
    search = SearchAlgorithm(database_size=500000, target_position=50000)
    
    print(f"\nDatabase Info:")
    info = search.get_database_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    results = search.run_comparison(platforms=['CPU', 'GPU'], shots=1024)
    speedups = search.calculate_speedup(results)
    
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    
    for platform, data in results['platforms'].items():
        if 'error' in data:
            print(f"\n{platform}: ERROR - {data['error']}")
            continue
            
        print(f"\n{platform}:")
        print(f"  Search Time: {data.get('search_time', 0):.4f}s")
        print(f"  Items/sec: {data.get('items_per_second', 0):.0f}")
        
        if platform in speedups:
            print(f"  Speedup vs CPU: {speedups[platform]:.2f}x")
    
    print("\n" + "="*80)
    
    return results

if __name__ == "__main__":
    # Run tests
    small_results = test_small_search()
    medium_results = test_medium_search()
    
    print("\n✓ All tests completed!")
