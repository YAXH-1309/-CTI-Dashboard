@echo off
echo Installing MongoDB Community Edition for Windows...
echo.

echo Step 1: Download MongoDB Community Edition
echo Please visit: https://www.mongodb.com/try/download/community
echo Select:
echo - Version: 7.0 (current)
echo - Platform: Windows
echo - Package: msi
echo.

echo Step 2: After download, run the .msi installer
echo - Choose "Complete" installation
echo - Install MongoDB as a Service (recommended)
echo - Install MongoDB Compass (optional GUI)
echo.

echo Step 3: Verify installation
echo After installation, MongoDB should start automatically as a Windows service
echo.

pause
echo.

echo Testing MongoDB connection...
mongosh --eval "db.runCommand({connectionStatus: 1})" 2>nul
if %errorlevel% equ 0 (
    echo ✓ MongoDB is running successfully!
) else (
    echo ✗ MongoDB not detected. Please complete the installation steps above.
    echo.
    echo Alternative: Use MongoDB Atlas (cloud) - see setup_atlas.bat
)

pause