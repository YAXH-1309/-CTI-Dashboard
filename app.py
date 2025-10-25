from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import threading
import time

from services.threat_intel import ThreatIntelService
from services.database import DatabaseService
from services.visualization import VisualizationService
from services.realtime_feeds import RealtimeFeedService

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cti-dashboard-secret-key')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize services
db_service = DatabaseService()
threat_service = ThreatIntelService(db_service)
viz_service = VisualizationService(db_service)
realtime_service = RealtimeFeedService(db_service, socketio)

# Background scheduler for periodic data fetching
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=threat_service.fetch_all_feeds,
    trigger="interval",
    hours=1,
    id='fetch_feeds'
)
scheduler.add_job(
    func=realtime_service.fetch_live_threats,
    trigger="interval",
    minutes=2,  # Check for new threats every 2 minutes
    id='realtime_feeds'
)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# Start real-time threat monitoring
realtime_service.start_monitoring()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/fetch-feeds', methods=['POST'])
def fetch_feeds():
    try:
        result = threat_service.fetch_all_feeds()
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/lookup', methods=['POST'])
def lookup_ioc():
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
    try:
        data = viz_service.get_dashboard_metrics()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/visuals/trends', methods=['GET'])
def get_trends():
    try:
        days = request.args.get('days', 7, type=int)
        data = viz_service.get_threat_trends(days)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/iocs', methods=['GET'])
def get_iocs():
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        search = request.args.get('search', '')
        tag_filter = request.args.get('tag', '')
        
        data = db_service.get_iocs_paginated(page, limit, search, tag_filter)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/iocs/<ioc_id>/tag', methods=['POST'])
def tag_ioc(ioc_id):
    try:
        data = request.get_json()
        tags = data.get('tags', [])
        
        result = db_service.update_ioc_tags(ioc_id, tags)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/export', methods=['GET'])
def export_data():
    try:
        format_type = request.args.get('format', 'json')
        days = request.args.get('days', 30, type=int)
        
        data = db_service.export_iocs(days, format_type)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/realtime/stats', methods=['GET'])
def get_realtime_stats():
    try:
        stats = realtime_service.get_live_stats()
        return jsonify({"status": "success", "data": stats})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/threat-ips', methods=['GET'])
def get_threat_ips():
    try:
        limit = request.args.get('limit', 100, type=int)
        classification = request.args.get('classification', '')
        
        # Get IP IOCs from database
        query = {"type": "ip"}
        if classification:
            query["classification"] = classification
        
        ips = list(db_service.iocs.find(query)
                  .sort("threat_score", -1)
                  .limit(limit))
        
        # Convert ObjectId to string
        for ip in ips:
            ip["_id"] = str(ip["_id"])
        
        return jsonify({"status": "success", "data": ips})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/threat-ips/<ip_address>/details', methods=['GET'])
def get_ip_threat_details(ip_address):
    try:
        # Get IP IOC from database
        ip_ioc = db_service.get_ioc(ip_address, 'ip')
        
        if not ip_ioc:
            return jsonify({"status": "error", "message": "IP not found"}), 404
        
        # Generate comprehensive threat intelligence data
        threat_details = threat_service.get_comprehensive_ip_data(ip_address, ip_ioc)
        
        return jsonify({"status": "success", "data": threat_details})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/threat-ips/<ip_address>/timeline', methods=['GET'])
def get_ip_threat_timeline(ip_address):
    try:
        # Get threat timeline for specific IP
        timeline = db_service.get_ip_threat_timeline(ip_address)
        
        return jsonify({"status": "success", "data": timeline})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected to real-time feed')
    emit('status', {'msg': 'Connected to CTI real-time feed'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from real-time feed')

@socketio.on('request_live_update')
def handle_live_update():
    stats = realtime_service.get_live_stats()
    emit('live_stats_update', stats)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)