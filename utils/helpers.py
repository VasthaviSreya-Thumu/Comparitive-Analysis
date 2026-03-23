"""
Helper functions for data formatting and utilities
"""

import time
import torch
import numpy as np
import subprocess
import sys

def format_bytes(bytes_value):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def set_seed(seed=42):
    """Set random seed for reproducibility"""
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

def _detect_gpu_windows():
    """Detect GPU on Windows using wmic (works for AMD, Intel, NVIDIA)."""
    try:
        result = subprocess.run(
            ["wmic", "path", "win32_VideoController", "get", "Name,AdapterRAM,DriverVersion", "/format:csv"],
            capture_output=True, text=True, timeout=5
        )
        lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip() and "Node" not in l]
        gpus = []
        for line in lines:
            parts = line.split(",")
            if len(parts) >= 3:
                ram_bytes = parts[1].strip()
                name = parts[2].strip()
                driver = parts[3].strip() if len(parts) > 3 else "N/A"
                if name:
                    ram_mb = int(ram_bytes) // (1024 * 1024) if ram_bytes.isdigit() else 0
                    gpus.append({'name': name, 'vram_mb': ram_mb, 'driver': driver})
        return gpus
    except Exception:
        return []

def get_device_info():
    """Get detailed device information, including AMD and Intel GPUs."""
    info = {
        'cpu_count': torch.get_num_threads(),
        'cuda_available': torch.cuda.is_available(),
        'gpu_available': False,
    }

    if torch.cuda.is_available():
        info['gpu_available'] = True
        info['gpu_count'] = torch.cuda.device_count()
        info['gpu_name'] = torch.cuda.get_device_name(0)
        info['cuda_version'] = torch.version.cuda
        info['cudnn_version'] = torch.backends.cudnn.version()
    else:
        # Fallback: detect GPU via OS-level query (AMD/Intel/any GPU on Windows)
        if sys.platform == "win32":
            gpus = _detect_gpu_windows()
            if gpus:
                info['gpu_available'] = True
                info['gpu_name'] = gpus[0]['name']
                info['gpu_vram_mb'] = gpus[0]['vram_mb']
                info['gpu_driver'] = gpus[0]['driver']
                info['gpu_backend'] = "DirectX/OpenCL (non-CUDA)"

    return info

def print_experiment_header(config_dict=None):
    """Print formatted experiment header"""
    print("\n" + "=" * 80)
    print("Search Comparison - Experiment Configuration")
    print("=" * 80)
    if config_dict:
        for key, value in config_dict.items():
            print(f"{key:30s}: {value}")
    print("=" * 80 + "\n")
