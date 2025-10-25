# 🚀 CTI Dashboard - Quick Start Guide

## Prerequisites ✅
- ✅ Docker installed and running
- ✅ Python 3.8+ installed
- ✅ Virtual environment created

## 🎯 One-Click Startup

### Option 1: Windows Batch File
```bash
start.bat
```

### Option 2: PowerShell
```powershell
.\start.ps1
```

### Option 3: Python Script
```bash
python quick_start.py
```

## 🔧 What the startup script does:

1. **✅ Checks Docker** - Verifies Docker is running
2. **🗄️ Starts MongoDB** - Launches MongoDB container on port 27017
3. **📦 Installs Dependencies** - Installs Python packages from requirements.txt
4. **⚙️ Sets up Environment** - Creates .env file if needed
5. **🚀 Launches Dashboard** - Starts the CTI Dashboard on http://localhost:5000

## 📊 Access Your Dashboard

Once started, open your browser and go to:
**http://localhost:5000**

## 🔴 Real-Time Features

- **Live threat feed** updates every 10 seconds
- **Real-time IP tracking** with geographic data
- **Interactive threat intelligence** for each IP
- **WebSocket connections** for instant updates

## 🛑 To Stop

Press `Ctrl+C` in the terminal to stop the application.
The script will automatically stop the MongoDB container.

## 🔧 Manual Commands (if needed)

### Start MongoDB manually:
```bash
docker run -d -p 27017:27017 --name cti-mongodb mongo:latest
```

### Stop MongoDB:
```bash
docker stop cti-mongodb
```

### Remove MongoDB container:
```bash
docker rm cti-mongodb
```

## 🎉 You're Ready!

Your CTI Dashboard will show:
- **Real-time threat detection**
- **IP threat intelligence**
- **Geographic threat mapping**
- **Attack pattern analysis**
- **Comprehensive threat data for each IP**

Enjoy your real-time cyber threat intelligence platform! 🛡️