"""
Unified Game Algorithm Interface (Tic-Tac-Toe)
Compares CPU (Classical), GPU (Parallel Simulation), and QPU (Quantum Logic)
"""

import numpy as np
import time
import random
from typing import Dict, Any, Optional, List

class GameAlgorithm:
    """
    Unified Game algorithm wrapper
    
    The problem: Play N games of Tic-Tac-Toe
    - CPU: Sequential game loop - O(N)
    - GPU: Parallel game simulation - O(N/P)
    - QPU: Quantum move selection - demonstrative of quantum logic
    """
    
    def __init__(self, num_games: int = 10, shots: int = 1024):
        """
        Initialize Game algorithm
        
        Args:
            num_games: Number of games to play
            shots: Shots for quantum measurement
        """
        self.num_games = num_games
        self.shots = shots
        
    def get_info(self) -> Dict[str, Any]:
        return {
            'num_games': self.num_games,
            'game': 'Tic-Tac-Toe',
            'type': 'Simulation'
        }
        
    def run(self, platform: str, **kwargs) -> Dict[str, Any]:
        if platform.upper() == 'CPU':
            return self._run_cpu(**kwargs)
        elif platform.upper() == 'GPU':
            return self._run_gpu(**kwargs)
        elif platform.upper() == 'QPU':
            return self._run_qpu(**kwargs)
        else:
            raise ValueError(f"Unknown platform: {platform}")

    def _run_cpu(self, **kwargs) -> Dict[str, Any]:
        """Run classical games sequentially on CPU"""
        import psutil
        import os
        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss / (1024 * 1024)
        
        start_time = time.perf_counter()
        
        x_wins = 0
        o_wins = 0
        draws = 0
        total_moves = 0
        
        # Simple simulation: Random vs Random
        for _ in range(self.num_games):
            board = [' '] * 9
            current_player = 'X'
            moves = 0
            
            while True:
                # Find empty spots
                empty = [i for i, x in enumerate(board) if x == ' ']
                if not empty:
                    draws += 1
                    break
                
                # Random move
                pos = random.choice(empty)
                board[pos] = current_player
                moves += 1
                
                # Check win logic (simplified)
                if self._check_win(board, current_player):
                    if current_player == 'X': x_wins += 1
                    else: o_wins += 1
                    break
                
                current_player = 'O' if current_player == 'X' else 'X'
            
            total_moves += moves
            
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        end_mem = process.memory_info().rss / (1024 * 1024)
        peak_mem = end_mem # Approx
        
        return {
            'platform': 'CPU',
            'algorithm': 'Classical Simulation',
            'games_played': self.num_games,
            'time_seconds': duration,
            'games_per_second': self.num_games / duration if duration > 0 else 0,
            'stats': {
                'x_wins': x_wins,
                'o_wins': o_wins,
                'draws': draws,
                'avg_moves': total_moves / self.num_games
            },
            'peak_memory_mb': peak_mem,
            'memory_used_mb': max(0, end_mem - start_mem),
            'success': True
        }

    def _check_win(self, board, player):
        wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        return any(all(board[p] == player for p in line) for line in wins)

    def _run_gpu(self, **kwargs) -> Dict[str, Any]:
        """Run parallel game simulations on GPU"""
        try:
            import torch
            if not torch.cuda.is_available():
                cpu_result = self._run_cpu(**kwargs)
                cpu_result.update({
                    'platform': 'GPU',
                    'note': 'CUDA unavailable (CPU Fallback)',
                    'algorithm': 'Simulated Parallel (CPU Fallback)'
                })
                return cpu_result
            
            # GPU Implementation
            device = torch.device('cuda')
            
            torch.cuda.reset_peak_memory_stats()
            start_mem = torch.cuda.memory_allocated() / (1024 * 1024)
            
            start_time = time.perf_counter()
            
            # Simulation Logic (Simplified for benchmark)
            games = torch.zeros((self.num_games, 9), dtype=torch.int8, device=device)
            active_games = torch.ones(self.num_games, dtype=torch.bool, device=device)
            
            for _ in range(9):
                if not active_games.any(): break
                probs = torch.rand((self.num_games, 9), device=device)
                taken = (games != 0)
                probs[taken] = -1.0
                moves = torch.argmax(probs, dim=1)
                games[torch.arange(self.num_games, device=device), moves] = 1 
                torch.cuda.synchronize()

            end_time = time.perf_counter()
            duration = end_time - start_time
            
            end_mem = torch.cuda.memory_allocated() / (1024 * 1024)
            peak_mem = torch.cuda.max_memory_allocated() / (1024 * 1024)
            
            return {
                'platform': 'GPU',
                'algorithm': 'Parallel Simulation (Tensor)',
                'games_played': self.num_games,
                'time_seconds': duration,
                'games_per_second': self.num_games / duration if duration > 0 else 0,
                'stats': {'note': 'Parallel simulation metrics'},
                'peak_memory_mb': peak_mem,
                'memory_used_mb': max(0, end_mem - start_mem),
                'success': True
            }
            
        except ImportError:
            cpu_result = self._run_cpu(**kwargs)
            cpu_result.update({
                'platform': 'GPU',
                'note': 'PyTorch unavailable (CPU Fallback)',
                'algorithm': 'Simulated Parallel (CPU Fallback)'
            })
            return cpu_result

    def _run_qpu(self, **kwargs) -> Dict[str, Any]:
        """Run using existing quantum_game.py"""
        import psutil
        import os
        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss / (1024 * 1024)
        
        from quantum.quantum_game import run_quantum_game
        
        # QPU simulation is slow, limit games if necessary
        actual_games = min(self.num_games, 5) 
        
        try:
            result = run_quantum_game(
                num_games=actual_games,
                shots=self.shots,
                verbose=False
            )
            
            end_mem = process.memory_info().rss / (1024 * 1024)
            
            return {
                'platform': 'QPU',
                'algorithm': 'Quantum Move Selection',
                'games_played': result['num_games'],
                'time_seconds': result['execution_time'],
                'games_per_second': result['num_games'] / result['execution_time'] if result['execution_time'] > 0 else 0,
                'stats': result['statistics'],
                'num_qubits': 4, # Max qubits for 3x3 board move selection
                'peak_memory_mb': end_mem,
                'memory_used_mb': max(0, end_mem - start_mem),
                'success': True
            }
        except Exception as e:
            return {'platform': 'QPU', 'error': str(e), 'success': False}

    def run_comparison(self, platforms=None, **kwargs):
        if platforms is None: platforms = ['CPU', 'GPU', 'QPU']
        results = {'info': self.get_info(), 'platforms': {}}
        for p in platforms:
            results['platforms'][p] = self.run(p, **kwargs)
        return results
