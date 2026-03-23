"""
Quantum Random Number Generator - True randomness from quantum mechanics
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np
import time

class QuantumRNG:
    """
    Quantum Random Number Generator using superposition
    """
    
    def __init__(self, num_qubits=5):
        """
        Args:
            num_qubits: Number of qubits (determines max random number = 2^n - 1)
        """
        self.num_qubits = num_qubits
        self.max_value = 2 ** num_qubits - 1
        self.circuit = None
        
    def build_circuit(self):
        """
        Build quantum circuit for random number generation
        Uses Hadamard gates to create equal superposition
        """
        # Create quantum and classical registers
        qr = QuantumRegister(self.num_qubits, 'q')
        cr = ClassicalRegister(self.num_qubits, 'c')
        qc = QuantumCircuit(qr, cr)
        
        # Apply Hadamard gates to all qubits (creates superposition)
        qc.h(range(self.num_qubits))
        
        # Measure all qubits
        qc.measure(qr, cr)
        
        self.circuit = qc
        return qc
    
    def generate_random_numbers(self, count=100, backend=None, shots=1):
        """
        Generate random numbers
        
        Args:
            count: How many random numbers to generate
            backend: Qiskit backend
            shots: Number of shots per circuit execution
        
        Returns:
            List of random numbers
        """
        from qiskit_aer import AerSimulator
        from qiskit import transpile
        
        # Use simulator if no backend provided
        if backend is None:
            backend = AerSimulator()
        
        # Build circuit
        circuit = self.build_circuit()
        transpiled = transpile(circuit, backend)
        
        # Check if using IBM Quantum backend or simulator
        is_ibm_backend = hasattr(backend, 'service') or 'ibm' in str(type(backend)).lower()
        
        random_numbers = []
        effective_shots = max(count, shots)
        
        if is_ibm_backend:
            # Use SamplerV2 for IBM Quantum backends
            from qiskit_ibm_runtime import SamplerV2 as Sampler
            
            # Run once with enough shots to get all numbers
            sampler = Sampler(mode=backend)
            job = sampler.run([transpiled], shots=effective_shots)
            result = job.result()
            
            # Extract bitstrings from SamplerV2 result
            pub_result = result[0]
            
            try:
                # Try to get bitstrings from the classical register
                if hasattr(pub_result.data, 'c'):
                    bitstrings = pub_result.data.c.get_bitstrings()
                elif hasattr(pub_result.data, 'meas'):
                    bitstrings = pub_result.data.meas.get_bitstrings()
                else:
                    # Get the first attribute that looks like measurement data
                    data_attrs = [attr for attr in dir(pub_result.data) if not attr.startswith('_')]
                    bitstrings = getattr(pub_result.data, data_attrs[0]).get_bitstrings()
                
                # Convert bitstrings to numbers
                for bitstring in bitstrings[:count]:
                    bitstring_str = ''.join(str(b) for b in bitstring)
                    random_numbers.append(int(bitstring_str, 2))
                    
            except Exception as e:
                print(f"Error extracting bitstrings: {e}")
                # Fallback: generate zeros
                random_numbers = [0] * count
                
        else:
            # Use a single batched Aer simulator run for significant speedup.
            job = backend.run(transpiled, shots=effective_shots, memory=True)
            result = job.result()

            try:
                bitstrings = result.get_memory()
                for bitstring in bitstrings[:count]:
                    random_numbers.append(int(bitstring, 2))
            except Exception:
                # Fallback when memory is unavailable: expand counts into a sample list.
                counts = result.get_counts()
                for bitstring, freq in counts.items():
                    random_numbers.extend([int(bitstring, 2)] * int(freq))

                if len(random_numbers) < count:
                    random_numbers.extend([0] * (count - len(random_numbers)))
                random_numbers = random_numbers[:count]
        
        return random_numbers
    
    def get_circuit_info(self):
        """Get circuit statistics"""
        if self.circuit is None:
            return None
        
        return {
            'num_qubits': self.num_qubits,
            'max_value': self.max_value,
            'circuit_depth': self.circuit.depth(),
            'gate_count': sum(self.circuit.count_ops().values())
        }


def run_quantum_rng(num_qubits=5, count=100, backend=None, shots=1024):
    """
    Run quantum random number generator
    
    Args:
        num_qubits: Number of qubits
        count: Number of random numbers to generate
        backend: Qiskit backend
        shots: Number of measurements (for IBM backends, shots=count is used)
    
    Returns:
        results dictionary
    """
    from qiskit_aer import AerSimulator
    
    start_time = time.perf_counter()
    
    # Create RNG
    rng = QuantumRNG(num_qubits)
    
    # Use simulator if no backend provided
    if backend is None:
        backend = AerSimulator()
    
    # Generate random numbers
    # For IBM backends, we use shots=count to get all numbers in one job.
    # For simulators, we also batch into one job for performance.
    is_ibm_backend = hasattr(backend, 'service') or 'ibm' in str(type(backend)).lower()
    actual_shots = count if is_ibm_backend else max(count, shots)
    
    numbers = rng.generate_random_numbers(count, backend, actual_shots)
    
    execution_time = time.perf_counter() - start_time
    
    # Calculate statistics
    if numbers:
        mean = np.mean(numbers)
        std = np.std(numbers)
        min_val = min(numbers)
        max_val = max(numbers)
        
        # Test for uniformity (chi-square test would be better)
        expected_mean = rng.max_value / 2
        uniformity_score = 1.0 - abs(mean - expected_mean) / expected_mean
    else:
        mean = std = min_val = max_val = 0
        uniformity_score = 0.0
    
    return {
        'algorithm': 'Quantum RNG',
        'num_qubits': num_qubits,
        'count': count,
        'numbers': numbers,
        'statistics': {
            'mean': mean,
            'std': std,
            'min': min_val,
            'max': max_val,
            'expected_mean': rng.max_value / 2,
            'uniformity_score': uniformity_score
        },
        'execution_time': execution_time,
        'circuit_info': rng.get_circuit_info(),
        'shots': actual_shots
    }


if __name__ == "__main__":
    # Test Quantum RNG
    print("Testing Quantum Random Number Generator...")
    
    result = run_quantum_rng(num_qubits=5, count=100, shots=1)
    
    print(f"\nGenerated {result['count']} random numbers")
    print(f"Range: 0 to {2**5 - 1}")
    print(f"Mean: {result['statistics']['mean']:.2f} (expected: {result['statistics']['expected_mean']:.2f})")
    print(f"Std Dev: {result['statistics']['std']:.2f}")
    print(f"Min: {result['statistics']['min']}, Max: {result['statistics']['max']}")
    print(f"Uniformity score: {result['statistics']['uniformity_score']:.2%}")
    print(f"Execution time: {result['execution_time']:.4f}s")
    print(f"\nFirst 10 numbers: {result['numbers'][:10]}")
    
