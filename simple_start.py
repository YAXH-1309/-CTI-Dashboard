#!/usr/bin/env python3
"""
Simple CTI Dashboard Startup - Without SocketIO for compatibility
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Try to import services, but handle gracefully if MongoDB is not available
try:
    from services.threat_intel import ThreatIntelService
    from services.database import DatabaseService
    from services.visualization import VisualizationService
    SERVICES_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Services not available: {e}")
    SERVICES_AVAILABLE = False

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cti-dashboard-secret-key')
CORS(app)

# Initialize services if available
if SERVICES_AVAILABLE:
    try:
        db_service = DatabaseService()
        threat_service = ThreatIntelService(db_service)
        viz_service = VisualizationService(db_service)
        print("✓ All services initialized successfully")
    except Exception as e:
        print(f"⚠️ Service initialization failed: {e}")
        SERVICES_AVAILABLE = False

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "success",
        "message": "CTI Dashboard is running",
        "services_available": SERVICES_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/fetch-feeds', methods=['POST'])
def fetch_feeds():
    if not SERVICES_AVAILABLE:
        return jsonify({"status": "error", "message": "Services not available"}), 503
    
    try:
        result = threat_service.fetch_all_feeds()
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/lookup', methods=['POST'])
def lookup_ioc():
    if not SERVICES_AVAILABLE:
        return jsonify({"status": "error", "message": "Services not available"}), 503
    
    try:
        data = request.get_json()
        ioc = data.get('ioc')
        ioc_type = data.get('type')
        
        if not ioc or not ioc_type:
            return jsonify({"status": "error", "message": "IOC and type required"}), 400
        
        result = threat_service.lookup_ioc(ioc, ioc_type)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/visuals/dashboard', methods=['GET'])
def get_dashboard_data():
    if not SERVICES_AVAILABLE:
        return jsonify({
            "status": "success", 
            "data": {
                "total_iocs": 0,
                "high_confidence": 0,
                "recent_threats": 0,
                "message": "Demo mode - MongoDB not connected"
            }
        })
    
    try:
        data = viz_service.get_dashboard_metrics()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("🛡️ CTI Dashboard - Simple Mode")
    print("=" * 50)
    print("🚀 Starting Flask application...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    if not SERVICES_AVAILABLE:
        print("⚠️ Running in demo mode - some features may be limited")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)