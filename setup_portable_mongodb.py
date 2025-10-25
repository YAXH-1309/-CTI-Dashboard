#!/usr/bin/env python3
"""
Portable MongoDB setup for CTI Dashboard
Downloads and runs MongoDB without installation
"""

import os
import sys
import zipfile
import requests
import subprocess
import time
from pathlib import Path

def download_mongodb():
    """Download portable MongoDB for Windows"""
    print("📥 Downloading MongoDB Community Edition...")
    
    # MongoDB download URL for Windows
    mongodb_url = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.4.zip"
    mongodb_zip = "mongodb.zip"
    
    try:
        response = requests.get(mongodb_url, stream=True)
        response.raise_for_status()
        
        with open(mongodb_zip, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("✓ MongoDB downloaded successfully")
        return mongodb_zip
    except Exception as e:
        print(f"❌ Error downloading MongoDB: {e}")
        return None

def extract_mongodb(zip_file):
    """Extract MongoDB archive"""
    print("📂 Extracting MongoDB...")
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Find the extracted directory
        for item in os.listdir("."):
            if item.startswith("mongodb-windows") and os.path.isdir(item):
                os.rename(item, "mongodb")
                break
        
        print("✓ MongoDB extracted to ./mongodb/")
        return True
    except Exception as e:
        print(f"❌ Error extracting MongoDB: {e}")
        return False

def setup_mongodb():
    """Setup MongoDB directories and configuration"""
    print("⚙️ Setting up MongoDB...")
    
    try:
        # Create data and log directories
        os.makedirs("mongodb/data", exist_ok=True)
        os.makedirs("mongodb/logs", exist_ok=True)
        
        # Create MongoDB configuration file
        config_content = """
systemLog:
  destination: file
  path: mongodb/logs/mongod.log
  logAppend: true
storage:
  dbPath: mongodb/data
net:
  port: 27017
  bindIp: 127.0.0.1
"""
        
        with open("mongodb/mongod.conf", "w") as f:
            f.write(config_content)
        
        print("✓ MongoDB configuration created")
        return True
    except Exception as e:
        print(f"❌ Error setting up MongoDB: {e}")
        return False

def start_mongodb():
    """Start MongoDB server"""
    print("🚀 Starting MongoDB server...")
    
    try:
        mongod_path = os.path.join("mongodb", "bin", "mongod.exe")
        config_path = os.path.join("mongodb", "mongod.conf")
        
        if not os.path.exists(mongod_path):
            print(f"❌ MongoDB executable not found at {mongod_path}")
            return None
        
        # Start MongoDB as a subprocess
        process = subprocess.Popen([
            mongod_path,
            "--config", config_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for MongoDB to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✓ MongoDB server started successfully")
            print("📊 MongoDB running on: mongodb://localhost:27017")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ MongoDB failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting MongoDB: {e}")
        return None

def main():
    """Main setup function"""
    print("🛡️ CTI Dashboard - MongoDB Portable Setup")
    print("=" * 50)
    
    # Check if MongoDB already exists
    if os.path.exists("mongodb/bin/mongod.exe"):
        print("✓ MongoDB already installed")
        process = start_mongodb()
        if process:
            print("\n🎉 MongoDB is ready!")
            print("You can now run: python run.py")
            print("\nPress Ctrl+C to stop MongoDB")
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n👋 Stopping MongoDB...")
                process.terminate()
        return
    
    # Download and setup MongoDB
    zip_file = download_mongodb()
    if not zip_file:
        return
    
    if not extract_mongodb(zip_file):
        return
    
    if not setup_mongodb():
        return
    
    # Clean up zip file
    try:
        os.remove(zip_file)
    except:
        pass
    
    # Start MongoDB
    process = start_mongodb()
    if process:
        print("\n🎉 MongoDB setup complete and running!")
        print("You can now run: python run.py")
        print("\nPress Ctrl+C to stop MongoDB")
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n👋 Stopping MongoDB...")
            process.terminate()

if __name__ == "__main__":
    main()