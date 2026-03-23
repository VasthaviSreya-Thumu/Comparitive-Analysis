@echo off
echo Starting Focus RNG Architecture Comparison Dashboard...
echo.
echo NOTE: If CUDA/PyTorch is unavailable, GPU path will use CPU fallback behavior.
echo NOTE: If Qiskit is unavailable, QPU path will show dependency errors.
echo.
set PYTHONIOENCODING=utf-8
python -m streamlit run app.py
pause
