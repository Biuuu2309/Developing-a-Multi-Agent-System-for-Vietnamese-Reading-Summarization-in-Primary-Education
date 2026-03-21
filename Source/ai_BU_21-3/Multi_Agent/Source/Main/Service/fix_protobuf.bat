@echo off
echo ========================================
echo Fixing protobuf compatibility issue
echo ========================================
echo.

REM Activate conda environment
call conda activate pytorch-env

echo Current protobuf version:
pip show protobuf

echo.
echo Downgrading protobuf to 3.20.3...
pip install protobuf==3.20.3

echo.
echo Done! Now try running flask_mas_api.py again.
pause

