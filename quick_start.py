#!/usr/bin/env python3
"""
Quick Start Script for CTI Dashboard
Starts MongoDB with Docker and launches the application
"""

import subprocess
import time
import sys
import os
from dotenv import load_dotenv

def print_banner():
    print("🛡️" + "=" * 60)
    print("   CTI Dashboard - Quick Start")
    print("   Real-Time Cyber Threat Intelligence Platform")
    print("=" * 62)
    print()

def check_docker():
    """Check if Docker is running"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✓ Docker detected: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not found or not running")
        print("Please make sure Docker Desktop is running")
        return False

def start_mongodb():
    """Start MongoDB using Docker"""
    print("🗄️ Starting MongoDB with Docker...")
    
    try:
        # Check if MongoDB container already exists
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=cti-mongodb'], 
                              capture_output=True, text=True)
        
        if 'cti-mongodb' in result.stdout:
            print("📦 MongoDB container exists, starting it...")
            subprocess.run(['docker', 'start', 'cti-mongodb'], check=True)
        else:
            print("📦 Creating new MongoDB container...")
            subprocess.run([
                'docker', 'run', '-d',
                '--name', 'cti-mongodb',
                '-p', '27017:27017',
                '-e', 'MONGO_INITDB_DATABASE=cti_dashboard',
                'mongo:latest'
            ], check=True)
        
        print("⏳ Waiting for MongoDB to be ready...")
        time.sleep(5)
        
        # Test MongoDB connection
        result = subprocess.run(['docker', 'exec', 'cti-mongodb', 'mongosh', '--eval', 'db.runCommand({ping: 1})'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ MongoDB is running and ready!")
            return True
        else:
            print("⚠️ MongoDB started but connection test failed")
            return True  # Continue anyway
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start MongoDB: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    if not os.path.exists('.env'):
        print("⚙️ Creating .env file...")
        with open('.env.example', 'r') as src, open('.env', 'w') as dst:
            dst.write(src.read())
        print("✓ .env file created")
        print("📝 You can add your API keys to .env file later")
    else:
        print("✓ .env file exists")
    
    load_dotenv()

def install_dependencies():
    """Install Python dependencies"""
    print("📚 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_application():
    """Start the CTI Dashboard application"""
    print("🚀 Starting CTI Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔴 Real-time threat monitoring will be active")
    print()
    print("Press Ctrl+C to stop the application")
    print("=" * 62)
    print()
    
    try:
        # Start the application
        subprocess.run([sys.executable, 'run.py'])
    except KeyboardInterrupt:
        print("\n👋 Stopping CTI Dashboard...")
        stop_services()
    except Exception as e:
        print(f"\n❌ Error running application: {e}")

def stop_services():
    """Stop MongoDB container"""
    print("🛑 Stopping MongoDB container...")
    try:
        subprocess.run(['docker', 'stop', 'cti-mongodb'], 
                      capture_output=True, check=True)
        print("✓ MongoDB stopped")
    except subprocess.CalledProcessError:
        print("⚠️ MongoDB container may already be stopped")

def main():
    """Main startup function"""
    print_banner()
    
    # Check prerequisites
    if not check_docker():
        print("\n💡 To install Docker:")
        print("   Visit: https://www.docker.com/products/docker-desktop")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start MongoDB
    if not start_mongodb():
        print("\n❌ Failed to start MongoDB")
        print("💡 Try running: docker run -d -p 27017:27017 --name cti-mongodb mongo:latest")
        sys.exit(1)
    
    print("\n🎉 All services ready!")
    print("🔗 MongoDB: mongodb://localhost:27017")
    print("🌐 Dashboard: http://localhost:5000")
    print()
    
    # Start the application
    start_application()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Startup cancelled by user")
        stop_services()
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        sys.exit(1)