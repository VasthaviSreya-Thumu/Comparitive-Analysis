"""
Quantum Tic-Tac-Toe - Using quantum superposition for move selection
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np
import random
import time

class QuantumTicTacToe:
    """
    Tic-Tac-Toe game where moves are selected using quantum randomness
    """
    
    def __init__(self):
        """Initialize game board"""
        self.board = [' ' for _ in range(9)]  # 3x3 board
        self.current_player = 'X'
        self.moves_history = []
        
    def reset(self):
        """Reset the game"""
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
        self.moves_history = []
        
    def available_moves(self):
        """Get list of available positions"""
        return [i for i, x in enumerate(self.board) if x == ' ']
    
    def make_move(self, position):
        """Make a move at the given position"""
        if self.board[position] == ' ':
            self.board[position] = self.current_player
            self.moves_history.append((self.current_player, position))
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            return True
        return False
    
    def check_winner(self):
        """
        Check if there's a winner
        Returns: 'X', 'O', 'Draw', or None
        """
        # Winning combinations
        wins = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        
        for combo in wins:
            if (self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != ' '):
                return self.board[combo[0]]
        
        # Check for draw
        if ' ' not in self.board:
            return 'Draw'
        
        return None
    
    def quantum_select_move(self, backend=None, shots=1024):
        """
        Select a move using quantum randomness
        
        Args:
            backend: Qiskit backend
            shots: Number of measurements
            
        Returns:
            Selected position (0-8)
        """
        from qiskit_aer import AerSimulator
        from qiskit import transpile
        
        available = self.available_moves()
        if not available:
            return None
        
        # If only one move available, return it
        if len(available) == 1:
            return available[0]
        
        # Calculate number of qubits needed
        num_positions = len(available)
        num_qubits = max(1, int(np.ceil(np.log2(num_positions))))
        
        # Create quantum circuit
        qr = QuantumRegister(num_qubits, 'q')
        cr = ClassicalRegister(num_qubits, 'c')
        qc = QuantumCircuit(qr, cr)
        
        # Create equal superposition
        qc.h(range(num_qubits))
        qc.measure(qr, cr)
        
        # Use simulator if no backend provided
        if backend is None:
            backend = AerSimulator()
        
        # Transpile circuit
        transpiled = transpile(qc, backend)
        
        # Check if using IBM Quantum backend or simulator
        is_ibm_backend = hasattr(backend, 'service') or 'ibm' in str(type(backend)).lower()
        
        if is_ibm_backend:
            # Use SamplerV2 for IBM Quantum backends
            from qiskit_ibm_runtime import SamplerV2 as Sampler
            
            sampler = Sampler(mode=backend)
            job = sampler.run([transpiled], shots=shots)
            result = job.result()
            
            # Extract counts from SamplerV2 result
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
                
                # Convert bitstrings to counts dictionary
                counts = {}
                for bitstring in bitstrings:
                    bitstring_str = ''.join(str(b) for b in bitstring)
                    counts[bitstring_str] = counts.get(bitstring_str, 0) + 1
                    
            except Exception as e:
                print(f"Error extracting counts: {e}")
                # Fallback: use random selection
                return random.choice(available)
                
        else:
            # Use Aer simulator
            job = backend.run(transpiled, shots=shots)
            result = job.result()
            counts = result.get_counts()
        
        # Find most common measurement that maps to valid position
        valid_counts = {}
        for bitstring, count in counts.items():
            index = int(bitstring, 2)
            if index < len(available):
                valid_counts[available[index]] = valid_counts.get(available[index], 0) + count
        
        if valid_counts:
            return max(valid_counts, key=valid_counts.get)
        else:
            # Fallback to random if no valid measurements
            return random.choice(available)
    
    def display_board(self):
        """Display the current board state"""
        print("\n")
        for i in range(0, 9, 3):
            print(f" {self.board[i]} | {self.board[i+1]} | {self.board[i+2]} ")
            if i < 6:
                print("-----------")
        print("\n")
    
    def get_board_state(self):
        """Get board as string for analysis"""
        return ''.join(self.board)


def run_quantum_game(num_games=5, backend=None, shots=1024, verbose=True):
    """
    Run multiple games of Quantum Tic-Tac-Toe
    
    Args:
        num_games: Number of games to play
        backend: Qiskit backend
        shots: Number of measurements per move
        verbose: Whether to print game progress
        
    Returns:
        results dictionary
    """
    from qiskit_aer import AerSimulator
    
    start_time = time.time()
    
    # Use simulator if no backend provided
    if backend is None:
        backend = AerSimulator()
    
    results = {
        'X_wins': 0,
        'O_wins': 0,
        'draws': 0,
        'total_moves': 0,
        'games': []
    }
    
    for game_num in range(num_games):
        game = QuantumTicTacToe()
        game_start = time.time()
        
        if verbose:
            print(f"\n{'='*50}")
            print(f"Game {game_num + 1}/{num_games}")
            print(f"{'='*50}")
        
        move_count = 0
        winner = None
        
        # Play until game ends
        while winner is None:
            if verbose:
                game.display_board()
                print(f"Player {game.current_player}'s turn...")
            
            # Quantum move selection
            position = game.quantum_select_move(backend, shots)
            
            if position is None:
                break
            
            game.make_move(position)
            move_count += 1
            
            if verbose:
                print(f"Quantum selected position: {position}")
            
            winner = game.check_winner()
        
        game_time = time.time() - game_start
        
        if verbose:
            game.display_board()
            print(f"Game Over! Winner: {winner if winner != 'Draw' else 'Draw'}")
            print(f"Moves: {move_count}, Time: {game_time:.2f}s")
        
        # Record results
        if winner == 'X':
            results['X_wins'] += 1
        elif winner == 'O':
            results['O_wins'] += 1
        else:
            results['draws'] += 1
        
        results['total_moves'] += move_count
        results['games'].append({
            'game_number': game_num + 1,
            'winner': winner,
            'moves': move_count,
            'time': game_time,
            'final_board': game.get_board_state(),
            'move_history': game.moves_history
        })
    
    execution_time = time.time() - start_time
    
    # Calculate statistics
    avg_moves = results['total_moves'] / num_games if num_games > 0 else 0
    
    return {
        'algorithm': 'Quantum Tic-Tac-Toe',
        'num_games': num_games,
        'results': results,
        'statistics': {
            'X_win_rate': results['X_wins'] / num_games if num_games > 0 else 0,
            'O_win_rate': results['O_wins'] / num_games if num_games > 0 else 0,
            'draw_rate': results['draws'] / num_games if num_games > 0 else 0,
            'avg_moves_per_game': avg_moves
        },
        'execution_time': execution_time,
        'shots': shots
    }


if __name__ == "__main__":
    # Test Quantum Tic-Tac-Toe
    print("Testing Quantum Tic-Tac-Toe...")
    
    result = run_quantum_game(num_games=3, shots=1024, verbose=True)
    
    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    print(f"Games played: {result['num_games']}")
    print(f"X wins: {result['results']['X_wins']}")
    print(f"O wins: {result['results']['O_wins']}")
    print(f"Draws: {result['results']['draws']}")
    print(f"Average moves per game: {result['statistics']['avg_moves_per_game']:.1f}")
    print(f"Total execution time: {result['execution_time']:.2f}s")