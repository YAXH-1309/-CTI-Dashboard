@echo off
title CTI Dashboard - Quick Start
cls

echo.
echo ========================================
echo    CTI Dashboard - Quick Start
echo    Real-Time Threat Intelligence
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

REM Run the quick start script
echo Starting CTI Dashboard...
python quick_start.py

pause