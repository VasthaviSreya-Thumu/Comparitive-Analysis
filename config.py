"""
Configuration file for Cross-Platform Search Algorithm Comparison
"""

import os
from pathlib import Path
import torch

# Project Paths
PROJECT_ROOT = Path(__file__).parent
LEGACY_DIR = PROJECT_ROOT / "legacy"
RESULTS_DIR = PROJECT_ROOT / "results"
LOGS_DIR = RESULTS_DIR / "logs"
CHARTS_DIR = RESULTS_DIR / "charts"
# REPORTS_DIR = RESULTS_DIR / "reports" # Optional

# Create directories if they don't exist
for directory in [RESULTS_DIR, LOGS_DIR, CHARTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Search Experiment Configuration
# Default parameters
DEFAULT_DATABASE_SIZE = 1000
DATABASE_SIZES = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000]
RANDOM_SEED = 42

# Memory Monitoring
MEMORY_SAMPLE_INTERVAL = 0.1  # seconds (faster sampling for search)

# QPU Configuration
DEFAULT_SHOTS = 1024
USE_REAL_QPU = False  # Set to True to use IBM Quantum hardware (requires account)

# Visualization
PLOT_DPI = 300
PLOT_STYLE = "seaborn-v0_8-darkgrid"
COLOR_PALETTE = "Set2"

# Hardware Detection
CUDA_AVAILABLE = torch.cuda.is_available()
try:
    DEVICE_NAME_GPU = torch.cuda.get_device_name(0) if CUDA_AVAILABLE else "N/A"
except Exception as e:
    DEVICE_NAME_GPU = "N/A"
GPU_COUNT = torch.cuda.device_count() if CUDA_AVAILABLE else 0

# Display Configuration
print("=" * 60)
print("Cross-Platform Search Comparison - Configuration")
print("=" * 60)
print(f"CUDA Available: {CUDA_AVAILABLE}")
if CUDA_AVAILABLE:
    print(f"GPU Device: {DEVICE_NAME_GPU}")
    print(f"GPU Count: {GPU_COUNT}")
print("=" * 60)
