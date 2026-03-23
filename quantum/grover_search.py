"""
Grover's Search Algorithm - Finding marked items in a database
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import GroverOperator
import numpy as np
import time

class GroverSearch:
    """
    Grover's algorithm implementation for searching in unstructured database
    """
    
    def __init__(self, num_qubits=3):
        """
        Args:
            num_qubits: Number of qubits (determines database size = 2^n)
        """
        self.num_qubits = num_qubits
        self.database_size = 2 ** num_qubits
        self.circuit = None
        self.marked_state = None
        
    def create_oracle(self, marked_state):
        """
        Create oracle that marks the target state
        
        Args:
            marked_state: Index to search for (0 to 2^n - 1)
        """
        self.marked_state = marked_state
        
        # Create quantum circuit
        qc = QuantumCircuit(self.num_qubits, name='Oracle')
        
        # Convert marked state to binary
        binary = format(marked_state, f'0{self.num_qubits}b')
        
        # Flip qubits where binary is 0
        for i, bit in enumerate(binary):
            if bit == '0':
                qc.x(i)
        
        # Multi-controlled Z gate
        qc.h(self.num_qubits - 1)
        qc.mcx(list(range(self.num_qubits - 1)), self.num_qubits - 1)
        qc.h(self.num_qubits - 1)
        
        # Unflip qubits
        for i, bit in enumerate(binary):
            if bit == '0':
                qc.x(i)
        
        return qc
    
    def create_diffusion(self):
        """Create diffusion operator (amplitude amplification)"""
        qc = QuantumCircuit(self.num_qubits, name='Diffusion')
        
        # Apply Hadamard gates
        qc.h(range(self.num_qubits))
        
        # Apply X gates
        qc.x(range(self.num_qubits))
        
        # Multi-controlled Z
        qc.h(self.num_qubits - 1)
        qc.mcx(list(range(self.num_qubits - 1)), self.num_qubits - 1)
        qc.h(self.num_qubits - 1)
        
        # Apply X gates
        qc.x(range(self.num_qubits))
        
        # Apply Hadamard gates
        qc.h(range(self.num_qubits))
        
        return qc
    
    def build_circuit(self, marked_state):
        """
        Build complete Grover's algorithm circuit
        
        Args:
            marked_state: State to search for
        """
        # Calculate optimal iterations
        iterations = int(np.pi / 4 * np.sqrt(self.database_size))
        
        # Create quantum and classical registers
        qr = QuantumRegister(self.num_qubits, 'q')
        cr = ClassicalRegister(self.num_qubits, 'c')
        qc = QuantumCircuit(qr, cr)
        
        # Initialize in equal superposition
        qc.h(range(self.num_qubits))
        qc.barrier()
        
        # Create oracle and diffusion operators
        oracle = self.create_oracle(marked_state)
        diffusion = self.create_diffusion()
        
        # Apply Grover iterations
        for _ in range(iterations):
            qc.append(oracle, range(self.num_qubits))
            qc.barrier()
            qc.append(diffusion, range(self.num_qubits))
            qc.barrier()
        
        # Measure
        qc.measure(qr, cr)
        
        self.circuit = qc
        return qc
    
    def get_circuit_info(self):
        """Get circuit statistics"""
        if self.circuit is None:
            return None
        
        return {
            'num_qubits': self.num_qubits,
            'database_size': self.database_size,
            'marked_state': self.marked_state,
            'circuit_depth': self.circuit.depth(),
            'gate_count': sum(self.circuit.count_ops().values()),
            'iterations': int(np.pi / 4 * np.sqrt(self.database_size))
        }


def run_grover_search(num_qubits=3, marked_state=5, backend=None, shots=1024):
    """
    Run Grover's search algorithm
    
    Args:
        num_qubits: Number of qubits
        marked_state: State to search for
        backend: Qiskit backend (simulator or real QPU)
        shots: Number of measurements
    
    Returns:
        results dictionary
    """
    from qiskit_aer import AerSimulator
    
    start_time = time.time()
    
    # Create Grover search
    grover = GroverSearch(num_qubits)
    circuit = grover.build_circuit(marked_state)
    
    # Use simulator if no backend provided
    if backend is None:
        backend = AerSimulator()
    
    # Transpile and run
    from qiskit import transpile
    transpiled = transpile(circuit, backend)
    
    # Check if using IBM Quantum backend or simulator
    is_ibm_backend = hasattr(backend, 'service') or 'ibm' in str(type(backend)).lower()
    
    if is_ibm_backend:
        # Use SamplerV2 for IBM Quantum backends
        from qiskit_ibm_runtime import SamplerV2 as Sampler
        
        sampler = Sampler(mode=backend)
        job = sampler.run([transpiled], shots=shots)
        result = job.result()
        
        # Extract counts from SamplerV2 result
        # SamplerV2 returns a PrimitiveResult with a list of PubResult objects
        pub_result = result[0]
        
        # Get the bitstring data
        # The measurement data is in pub_result.data.c (or the classical register name)
        try:
            # Try to get counts from the classical register
            if hasattr(pub_result.data, 'c'):
                bitstrings = pub_result.data.c.get_bitstrings()
            elif hasattr(pub_result.data, 'meas'):
                bitstrings = pub_result.data.meas.get_bitstrings()
            else:
                # Get the first attribute that looks like measurement data
                data_attrs = [attr for attr in dir(pub_result.data) if not attr.startswith('_')]
                bitstrings = getattr(pub_result.data, data_attrs[0]).get_bitstrings()
            
            # Convert bitstrings to counts dictionary
            counts = {}
            for bitstring in bitstrings:
                bitstring_str = ''.join(str(b) for b in bitstring)
                counts[bitstring_str] = counts.get(bitstring_str, 0) + 1
                
        except Exception as e:
            print(f"Error extracting counts: {e}")
            # Fallback: create empty counts
            counts = {}
            
    else:
        # Use Aer simulator's run method
        job = backend.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()
    
    execution_time = time.time() - start_time
    
    # Handle empty counts
    if not counts:
        print("Warning: No measurement results obtained")
        return {
            'algorithm': 'Grover Search',
            'num_qubits': num_qubits,
            'database_size': 2 ** num_qubits,
            'marked_state': marked_state,
            'found_state': None,
            'success': False,
            'success_probability': 0.0,
            'execution_time': execution_time,
            'circuit_info': grover.get_circuit_info(),
            'measurement_counts': {},
            'shots': shots,
            'error': 'No measurement results'
        }
    
    # Find most common result
    most_common = max(counts, key=counts.get)
    
    # Qiskit uses little-endian ordering (qubit 0 is LSB of the string),
    # but our oracle encoding put the MSB on qubit 0.
    # So we need to reverse the bitstring to get the correct integer.
    most_common_decimal = int(most_common[::-1], 2)
    
    # Calculate success probability
    # Determine the expected key (reversed because of Qiskit ordering)
    expected_key = format(marked_state, f'0{num_qubits}b')[::-1]
    success_probability = counts.get(expected_key, 0) / shots
    
    return {
        'algorithm': 'Grover Search',
        'num_qubits': num_qubits,
        'database_size': 2 ** num_qubits,
        'marked_state': marked_state,
        'found_state': most_common_decimal,
        'success': (most_common_decimal == marked_state),
        'success_probability': success_probability,
        'execution_time': execution_time,
        'circuit_info': grover.get_circuit_info(),
        'measurement_counts': counts,
        'shots': shots
    }


if __name__ == "__main__":
    # Test Grover's algorithm
    print("Testing Grover's Search Algorithm...")
    
    result = run_grover_search(num_qubits=3, marked_state=5, shots=1024)
    
    print(f"\nSearching for state: {result['marked_state']}")
    print(f"Found state: {result['found_state']}")
    print(f"Success: {result['success']}")
    print(f"Success probability: {result['success_probability']:.2%}")
    print(f"Execution time: {result['execution_time']:.4f}s")
    print(f"Circuit depth: {result['circuit_info']['circuit_depth']}")
    print(f"Total gates: {result['circuit_info']['gate_count']}")