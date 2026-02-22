@echo off
echo ========================================
echo Starting Flask MAS API
echo ========================================
echo.

REM Activate conda environment
call conda activate pytorch-env

REM Di chuyển đến thư mục hiện tại (nơi file .bat đang ở)
cd /d "%~dp0"

echo Current directory: %CD%
echo.

echo Installing/updating dependencies...
python -m pip install -r requirements.txt

echo.
echo ========================================
echo Starting Flask API Server...
echo ========================================
echo.
python flask_mas_api.py

pause

