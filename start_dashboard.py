#!/usr/bin/env python3
"""
CTI Dashboard Quick Start Script
Handles setup and launches the real-time dashboard
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🛡️  CTI Dashboard - Real-Time Threat Intelligence")
    print("=" * 60)
    print()

def check_python():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print("✓ Python version:", sys.version.split()[0])
    return True

def setup_venv():
    """Setup virtual environment"""
    if not os.path.exists("venv"):
        print("📦 Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✓ Virtual environment created")
        except subprocess.CalledProcessError:
            print("❌ Failed to create virtual environment")
            return False
    else:
        print("✓ Virtual environment exists")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📚 Installing dependencies...")
    
    # Determine pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = os.path.join("venv", "Scripts", "pip.exe")
        python_path = os.path.join("venv", "Scripts", "python.exe")
    else:  # Unix/Linux/Mac
        pip_path = os.path.join("venv", "bin", "pip")
        python_path = os.path.join("venv", "bin", "python")
    
    try:
        # Upgrade pip first
        subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Install requirements
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_env_file():
    """Setup environment file"""
    if not os.path.exists(".env"):
        print("⚙️ Creating .env file from template...")
        try:
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("✓ .env file created")
            print()
            print("⚠️  IMPORTANT: Please add your API keys to .env file:")
            print("   - VirusTotal API: https://www.virustotal.com/gui/join-us")
            print("   - AbuseIPDB API: https://www.abuseipdb.com/api")
            print()
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("✓ .env file exists")
    return True

def check_mongodb():
    """Check if MongoDB is available"""
    print("🗄️ Checking MongoDB...")
    
    # Try to connect to MongoDB
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✓ MongoDB is running")
        return True
    except Exception:
        print("⚠️ MongoDB not detected")
        return setup_portable_mongodb()

def setup_portable_mongodb():
    """Setup portable MongoDB if needed"""
    print("📥 Setting up portable MongoDB...")
    
    if os.path.exists("mongodb"):
        print("✓ Portable MongoDB found")
        return start_portable_mongodb()
    
    print("Would you like to:")
    print("1. Download and setup portable MongoDB (recommended)")
    print("2. Use MongoDB Atlas (cloud database)")
    print("3. Install MongoDB locally")
    print("4. Continue without MongoDB (limited functionality)")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        return download_portable_mongodb()
    elif choice == "2":
        print_atlas_instructions()
        return True
    elif choice == "3":
        print_local_mongodb_instructions()
        return True
    else:
        print("⚠️ Continuing without MongoDB - some features will be limited")
        return True

def download_portable_mongodb():
    """Download and setup portable MongoDB"""
    try:
        print("📥 Downloading MongoDB (this may take a few minutes)...")
        
        # Run the portable MongoDB setup
        if os.name == 'nt':  # Windows
            python_path = os.path.join("venv", "Scripts", "python.exe")
        else:
            python_path = os.path.join("venv", "bin", "python")
        
        result = subprocess.run([python_path, "setup_portable_mongodb.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Portable MongoDB setup complete")
            return True
        else:
            print(f"❌ MongoDB setup failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up MongoDB: {e}")
        return False

def start_portable_mongodb():
    """Start portable MongoDB"""
    try:
        mongod_path = os.path.join("mongodb", "bin", "mongod.exe" if os.name == 'nt' else "mongod")
        config_path = os.path.join("mongodb", "mongod.conf")
        
        if os.path.exists(mongod_path):
            print("🚀 Starting portable MongoDB...")
            subprocess.Popen([mongod_path, "--config", config_path], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)  # Give MongoDB time to start
            print("✓ MongoDB started")
            return True
    except Exception as e:
        print(f"❌ Failed to start MongoDB: {e}")
    return False

def print_atlas_instructions():
    """Print MongoDB Atlas setup instructions"""
    print()
    print("📋 MongoDB Atlas Setup:")
    print("1. Visit: https://www.mongodb.com/cloud/atlas/register")
    print("2. Create a free cluster")
    print("3. Create database user and configure network access")
    print("4. Get connection string and update MONGODB_URI in .env")
    print()

def print_local_mongodb_instructions():
    """Print local MongoDB installation instructions"""
    print()
    print("📋 Local MongoDB Installation:")
    print("1. Visit: https://www.mongodb.com/try/download/community")
    print("2. Download and install MongoDB Community Edition")
    print("3. Start MongoDB service")
    print()

def start_dashboard():
    """Start the CTI Dashboard"""
    print("🚀 Starting CTI Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔴 Real-time threat monitoring will be active")
    print()
    print("Press Ctrl+C to stop the dashboard")
    print("=" * 60)
    
    try:
        # Determine Python path
        if os.name == 'nt':  # Windows
            python_path = os.path.join("venv", "Scripts", "python.exe")
        else:
            python_path = os.path.join("venv", "bin", "python")
        
        # Start the dashboard
        subprocess.run([python_path, "run.py"])
        
    except KeyboardInterrupt:
        print("\n👋 CTI Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")

def main():
    """Main function"""
    print_banner()
    
    # Check prerequisites
    if not check_python():
        sys.exit(1)
    
    if not setup_venv():
        sys.exit(1)
    
    if not install_dependencies():
        sys.exit(1)
    
    if not setup_env_file():
        sys.exit(1)
    
    check_mongodb()  # MongoDB is optional
    
    print()
    print("🎉 Setup complete! Starting dashboard...")
    print()
    
    # Start the dashboard
    start_dashboard()

if __name__ == "__main__":
    main()