#!/usr/bin/env python3
"""
CTI Dashboard Startup Script
Handles environment setup and application initialization
"""

import os
import sys
from dotenv import load_dotenv

def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import flask
        import pymongo
        import requests
        print("✓ All Python dependencies are available")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_mongodb():
    """Check MongoDB connection"""
    try:
        from pymongo import MongoClient
        client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        client.server_info()
        print("✓ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        print("Please ensure MongoDB is running")
        return False

def check_api_keys():
    """Check if API keys are configured"""
    vt_key = os.getenv('VIRUSTOTAL_API_KEY')
    abuse_key = os.getenv('ABUSEIPDB_API_KEY')
    
    if not vt_key:
        print("⚠ VirusTotal API key not configured")
        print("Set VIRUSTOTAL_API_KEY in .env file")
    else:
        print("✓ VirusTotal API key configured")
    
    if not abuse_key:
        print("⚠ AbuseIPDB API key not configured")
        print("Set ABUSEIPDB_API_KEY in .env file")
    else:
        print("✓ AbuseIPDB API key configured")
    
    return bool(vt_key or abuse_key)

def main():
    """Main startup function"""
    print("🛡️  CTI Dashboard - Starting up...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check all prerequisites
    checks_passed = 0
    total_checks = 3
    
    if check_dependencies():
        checks_passed += 1
    
    if check_mongodb():
        checks_passed += 1
    
    if check_api_keys():
        checks_passed += 1
    
    print("=" * 50)
    print(f"Startup checks: {checks_passed}/{total_checks} passed")
    
    if checks_passed < 2:
        print("❌ Critical checks failed. Please fix the issues above.")
        sys.exit(1)
    
    if checks_passed < total_checks:
        print("⚠️  Some checks failed. The application may have limited functionality.")
    
    print("🚀 Starting CTI Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("=" * 50)
    
    # Import and run the Flask app with SocketIO
    try:
        from app import app, socketio
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 CTI Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()