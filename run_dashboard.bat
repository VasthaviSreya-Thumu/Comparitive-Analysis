@echo off
echo Starting Cross-Platform Search Algorithm Dashboard...
echo.
echo NOTE: If you have an AMD GPU, this application will run in CPU fallback mode
echo because standard PyTorch only supports NVIDIA CUDA.
echo.
set PYTHONIOENCODING=utf-8
python -m streamlit run app.py
pause
