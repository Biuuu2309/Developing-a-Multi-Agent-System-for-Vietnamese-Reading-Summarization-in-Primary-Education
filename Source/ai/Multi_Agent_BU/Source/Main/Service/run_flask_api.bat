@echo off
echo ========================================
echo Starting Flask MAS API with Conda
echo ========================================
echo.

REM Thử các đường dẫn conda thường gặp
set CONDA_BASE=%USERPROFILE%\anaconda3
if not exist "%CONDA_BASE%" set CONDA_BASE=%USERPROFILE%\miniconda3
if not exist "%CONDA_BASE%" set CONDA_BASE=C:\ProgramData\anaconda3
if not exist "%CONDA_BASE%" set CONDA_BASE=C:\ProgramData\miniconda3

echo Looking for Conda at: %CONDA_BASE%

if not exist "%CONDA_BASE%\Scripts\activate.bat" (
    echo ERROR: Cannot find Conda installation!
    echo Please edit this file and set CONDA_BASE to your Conda path
    echo.
    echo Common locations:
    echo   - %USERPROFILE%\anaconda3
    echo   - %USERPROFILE%\miniconda3
    echo   - C:\ProgramData\anaconda3
    echo.
    pause
    exit /b 1
)

echo Activating conda environment: pytorch-env
call "%CONDA_BASE%\Scripts\activate.bat" pytorch-env

if errorlevel 1 (
    echo ERROR: Failed to activate pytorch-env
    echo Please make sure the environment exists: conda env list
    pause
    exit /b 1
)

echo.
echo Environment activated: pytorch-env
echo Current directory: %CD%
echo.

REM Di chuyển đến thư mục Service nếu chưa ở đó
cd /d "%~dp0"

echo Installing/updating dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo WARNING: Some packages may have failed to install
    echo Continuing anyway...
    echo.
)

echo.
echo ========================================
echo Starting Flask API Server...
echo ========================================
echo.

REM Set environment variable to fix protobuf issue
set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

python flask_mas_api.py

pause

