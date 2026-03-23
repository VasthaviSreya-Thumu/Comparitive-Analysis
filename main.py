"""
RNG Comparison CLI (CPU vs GPU vs QPU)

This is the minimal command-line runner aligned to the project problem statement.
"""

import argparse
import sys
from typing import Dict, Any

from algorithms.rng_algorithm import RNGAlgorithm
from utils.helpers import get_device_info, set_seed


def print_banner() -> None:
    print("\n" + "=" * 80)
    print(" " * 19 + "Focus RNG Architecture Comparison (CLI)")
    print(" " * 15 + "CPU vs GPU vs QPU - Time and Resource Efficiency")
    print("=" * 80 + "\n")


def print_environment() -> None:
    info = get_device_info()
    print("Environment Check:")
    print("-" * 80)
    print(f"CPU Threads: {info.get('cpu_count', 'Unknown')}")
    print(f"CUDA Available: {info.get('cuda_available', False)}")
    if info.get("gpu_available"):
        print(f"GPU: {info.get('gpu_name', 'Unknown')}")
    else:
        print("! GPU not available. GPU path may run as CPU fallback.")
    print("-" * 80 + "\n")


def run_rng(count: int, qubits: int, shots: int, seed: int) -> Dict[str, Any]:
    set_seed(seed)
    runner = RNGAlgorithm(count=count, num_qubits=qubits, seed=seed)
    return runner.run_comparison(platforms=["CPU", "GPU", "QPU"], shots=shots)


def print_summary(results: Dict[str, Any], count: int, qubits: int) -> None:
    print(f"RNG Run: N={count}, qubits={qubits}")
    print("-" * 80)
    for platform, data in results.get("platforms", {}).items():
        if data.get("success"):
            t = float(data.get("generation_time", 0.0) or 0.0)
            r = float(data.get("numbers_per_second", 0.0) or 0.0)
            mem = data.get("peak_memory_mb")
            label = data.get("algorithm", "Unknown")
            print(f"[OK] {platform:>3} | {label}")
            print(f"     time={t:.6f}s | throughput={r:,.2f}/s")
            if platform == "QPU":
                print(f"     qubits={data.get('num_qubits', qubits)}")
            else:
                print(f"     peak_memory_mb={mem if mem is not None else 'N/A'}")
        else:
            print(f"[FAIL] {platform:>3} | {data.get('error', 'Unknown error')}")
    print("-" * 80)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CPU vs GPU vs QPU RNG comparison (problem-statement aligned)."
    )
    parser.add_argument("--count", type=int, default=1000, help="Number of random values to generate.")
    parser.add_argument("--qubits", type=int, default=8, help="Qubits for QPU RNG range.")
    parser.add_argument("--shots", type=int, default=1024, help="Quantum measurement shots.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.count <= 0:
        print("Count must be > 0")
        return 2
    if args.qubits < 2:
        print("Qubits must be >= 2")
        return 2

    print_banner()
    print_environment()

    try:
        results = run_rng(
            count=args.count,
            qubits=args.qubits,
            shots=args.shots,
            seed=args.seed,
        )
        print_summary(results, count=args.count, qubits=args.qubits)
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except Exception as exc:
        print(f"\nError: {exc}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

