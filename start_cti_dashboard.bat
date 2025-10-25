@echo off
title CTI Dashboard Startup
echo 🛡️ CTI Dashboard - Automated Setup
echo ================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚙️ Creating .env file from template...
    copy .env.example .env
    echo.
    echo ⚠️ IMPORTANT: Please edit .env file with your API keys:
    echo - Get VirusTotal API key from: https://www.virustotal.com/gui/join-us
    echo - Get AbuseIPDB API key from: https://www.abuseipdb.com/api
    echo.
    pause
)

REM Check MongoDB options
echo 🗄️ Checking MongoDB setup...

REM Option 1: Check if MongoDB service is running
sc query "MongoDB" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ MongoDB service detected
    goto :start_app
)

REM Option 2: Check if portable MongoDB exists
if exist "mongodb\bin\mongod.exe" (
    echo ✓ Portable MongoDB found
    echo 🚀 Starting portable MongoDB...
    start /b mongodb\bin\mongod.exe --config mongodb\mongod.conf
    timeout /t 3 >nul
    goto :start_app
)

REM Option 3: Setup portable MongoDB
echo 📥 Setting up portable MongoDB...
python setup_portable_mongodb.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ MongoDB setup failed. Please try one of these options:
    echo 1. Run: install_mongodb.bat (for local installation)
    echo 2. Run: setup_atlas.bat (for cloud database)
    echo 3. Install Docker Desktop and run: docker run -d -p 27017:27017 mongo:latest
    pause
    exit /b 1
)

:start_app
echo.
echo 🎯 Starting CTI Dashboard...
echo Dashboard will be available at: http://localhost:5000
echo.
python run.py

pause