"""
QPU Quantum Search Implementation
Wrapper for Grover's algorithm to match unified search interface
"""

import time
from typing import Dict, Any
from quantum.grover_search import GroverSearch


class QPUSearch:
    """
    QPU-based quantum search using Grover's algorithm
    Complexity: O(√N) - quadratic speedup over classical search
    """
    
    def __init__(self, database_size: int, target_position: int):
        """
        Initialize QPU search
        
        Args:
            database_size: Size of search space (must be power of 2 for Grover)
            target_position: Index of target item
        """
        self.database_size = database_size
        self.target_position = target_position
        
        # Calculate number of qubits needed
        import math
        self.num_qubits = max(2, int(math.ceil(math.log2(database_size))))
        
        # Adjust database size to nearest power of 2
        self.adjusted_size = 2 ** self.num_qubits
        
    def search(self, shots: int = 1024, use_real_qpu: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Perform quantum search using Grover's algorithm
        
        Args:
            shots: Number of measurement shots
            use_real_qpu: Whether to use real IBM Quantum hardware
            **kwargs: Additional arguments to match interface (e.g. monitor)
            
        Returns:
            Dictionary with search results and metrics
        """
        start_time = time.time()
        
        # Create Grover search instance
        grover = GroverSearch(num_qubits=self.num_qubits)
        
        # Run using helper function from grover_search module or manual execution
        # Here we use the run_grover_search helper for consistency if available,
        # or implement logic to use the class directly
        
        from quantum.grover_search import run_grover_search
        
        result = run_grover_search(
            num_qubits=self.num_qubits,
            marked_state=self.target_position,
            backend=None, # Todo: pass backend if needed or use_real_qpu logic
            shots=shots
        )
        
        # Map result keys to what we expect if needed, currently run_grover_search returns compatible dict except 'iterations' vs 'grover_iterations'
        end_time = time.time()
        search_time = end_time - start_time
        
        # Check if we need to adapt the result from run_grover_search
        found = result.get('success', False)
        measured_state = result.get('found_state', -1)
        success_probability = result.get('success_probability', 0.0)
        
        # Helper to get circuit stats
        circuit_info = result.get('circuit_info', {})
        circuit_depth = circuit_info.get('circuit_depth', 0) if circuit_info else 0
        gate_count = circuit_info.get('gate_count', 0) if circuit_info else 0
        grover_iterations = circuit_info.get('iterations', 0) if circuit_info else 0

        # Calculate theoretical metrics
        import math
        theoretical_iterations = int(math.pi / 4 * math.sqrt(self.adjusted_size))
        
        return {
            'platform': 'QPU',
            'algorithm': "Grover's Search",
            'complexity': 'O(√N)',
            'found': found,
            'found_position': measured_state if found else -1,
            'target_position': self.target_position,
            'success_probability': success_probability,
            'search_time': search_time,
            'database_size': self.database_size,
            'adjusted_size': self.adjusted_size,
            'num_qubits': self.num_qubits,
            'circuit_depth': circuit_depth,
            'gate_count': gate_count,
            'grover_iterations': grover_iterations,
            'theoretical_iterations': theoretical_iterations,
            'shots': shots,
            'backend': 'simulator', # Default for now
            'use_real_qpu': use_real_qpu,
            'quantum_speedup_factor': math.sqrt(self.adjusted_size) / grover_iterations if grover_iterations > 0 else 0,
            'success': found
        }
    
    def search_with_analysis(self, shots: int = 1024) -> Dict[str, Any]:
        """
        Perform search with detailed quantum analysis
        
        Args:
            shots: Number of measurement shots
            
        Returns:
            Dictionary with detailed quantum metrics
        """
        result = self.search(shots=shots)
        
        # Add theoretical analysis
        import math
        N = self.adjusted_size
        sqrt_N = math.sqrt(N)
        
        result['theoretical_analysis'] = {
            'classical_complexity': f'O({N})',
            'quantum_complexity': f'O({sqrt_N:.1f})',
            'theoretical_speedup': N / sqrt_N,
            'amplitude_amplification_factor': sqrt_N,
            'success_probability_theoretical': 1.0 - (1.0 / N)
        }
        
        return result
