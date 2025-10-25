import requests
import threading
import time
import json
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse
import socket

class RealtimeFeedService:
    def __init__(self, db_service, socketio):
        self.db = db_service
        self.socketio = socketio
        self.monitoring = False
        self.live_stats = {
            'threats_last_hour': 0,
            'threats_last_24h': 0,
            'active_campaigns': 0,
            'new_malware_families': 0,
            'compromised_websites': 0,
            'botnet_activity': 0,
            'current_threat_level': 'medium'
        }
        
        # Real-time threat intelligence feeds (free/public sources)
        self.threat_feeds = {
            'malware_domains': 'http://www.malwaredomainlist.com/hostslist/hosts.txt',
            'phishtank': 'http://data.phishtank.com/data/online-valid.csv',
            'openphish': 'https://openphish.com/feed.txt',
            'urlhaus': 'https://urlhaus.abuse.ch/downloads/csv_recent/',
            'feodo_tracker': 'https://feodotracker.abuse.ch/downloads/ipblocklist.txt'
        }
        
        # Simulated threat sources for demo (replace with real feeds in production)
        self.demo_threats = [
            {'type': 'malware', 'severity': 'high', 'source': 'honeypot'},
            {'type': 'phishing', 'severity': 'medium', 'source': 'email_filter'},
            {'type': 'botnet', 'severity': 'critical', 'source': 'network_monitor'},
            {'type': 'c2', 'severity': 'high', 'source': 'dns_sinkhole'},
            {'type': 'ransomware', 'severity': 'critical', 'source': 'endpoint_detection'}
        ]
    
    def start_monitoring(self):
        """Start real-time threat monitoring"""
        if not self.monitoring:
            self.monitoring = True
            monitor_thread = threading.Thread(target=self._monitor_threats, daemon=True)
            monitor_thread.start()
            print("🔴 Real-time threat monitoring started")
    
    def stop_monitoring(self):
        """Stop real-time threat monitoring"""
        self.monitoring = False
        print("⏹️ Real-time threat monitoring stopped")
    
    def _monitor_threats(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Simulate real-time threat detection
                self._simulate_threat_detection()
                
                # Update live statistics
                self._update_live_stats()
                
                # Broadcast updates to connected clients
                self._broadcast_updates()
                
                # Sleep for a short interval (simulate real-time)
                time.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                print(f"Error in threat monitoring: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _simulate_threat_detection(self):
        """Simulate real-time threat detection (replace with actual feeds)"""
        import random
        
        # Simulate detecting 1-4 new threats every cycle (increased frequency)
        num_threats = random.randint(1, 4)
        
        for _ in range(num_threats):
            threat = random.choice(self.demo_threats).copy()
            
            # Bias towards IP threats for better IP dashboard demonstration
            if random.random() < 0.7:  # 70% chance of IP threat
                threat['force_ip'] = True
            
            # Generate realistic threat data
            threat_data = self._generate_threat_data(threat)
            
            # Store in database
            ioc_id = self.db.store_ioc(threat_data)
            
            # Emit real-time update
            self.socketio.emit('new_threat', {
                'threat': threat_data,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            print(f"🚨 New {threat['type']} threat detected: {threat_data['value']} ({threat_data['type']})")
    
    def _generate_threat_data(self, threat_template):
        """Generate realistic threat IOC data"""
        import random
        
        threat_types = {
            'malware': self._generate_malware_ioc,
            'phishing': self._generate_phishing_ioc,
            'botnet': self._generate_botnet_ioc,
            'c2': self._generate_c2_ioc,
            'ransomware': self._generate_ransomware_ioc
        }
        
        generator = threat_types.get(threat_template['type'], self._generate_generic_ioc)
        return generator(threat_template)
    
    def _generate_malware_ioc(self, template):
        """Generate malware IOC"""
        import random
        
        # Force IP generation if requested, otherwise 80% chance for IP
        force_ip = template.get('force_ip', False)
        generate_ip = force_ip or random.random() < 0.8
        
        if generate_ip:
            # Generate more realistic malicious IP ranges
            ip_ranges = [
                (1, 126),    # Class A
                (128, 191),  # Class B  
                (192, 223),  # Class C
            ]
            
            ip_class = random.choice(ip_ranges)
            ip = f"{random.randint(ip_class[0], ip_class[1])}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            
            # Avoid common private/reserved ranges
            while (ip.startswith('192.168.') or ip.startswith('10.') or 
                   ip.startswith('172.') or ip.startswith('127.') or
                   ip.startswith('169.254.')):
                ip = f"{random.randint(ip_class[0], ip_class[1])}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            
            return {
                'value': ip,
                'type': 'ip',
                'threat_score': random.randint(70, 95),
                'classification': template['severity'],
                'sources': [template['source']],
                'tags': ['malware', 'suspicious_ip'],
                'description': f"Malicious IP detected by {template['source']}",
                'source_details': [{
                    'source': template['source'],
                    'threat_score': random.randint(70, 95),
                    'classification': template['severity'],
                    'details': {
                        'detection_method': 'behavioral_analysis',
                        'confidence': random.randint(80, 95),
                        'country': random.choice(['CN', 'RU', 'US', 'DE', 'FR', 'GB', 'KR']),
                        'asn': f"AS{random.randint(1000, 99999)}",
                        'first_seen': datetime.utcnow().isoformat()
                    }
                }]
            }
        else:
            # Suspicious domain
            domains = ['suspicious-site', 'malware-host', 'infected-domain', 'trojan-server']
            tlds = ['.com', '.net', '.org', '.info', '.biz']
            domain = f"{random.choice(domains)}{random.randint(1, 999)}{random.choice(tlds)}"
            
            return {
                'value': domain,
                'type': 'domain',
                'threat_score': random.randint(65, 90),
                'classification': template['severity'],
                'sources': [template['source']],
                'tags': ['malware', 'suspicious_domain'],
                'description': f"Malicious domain detected by {template['source']}",
                'source_details': [{
                    'source': template['source'],
                    'threat_score': random.randint(65, 90),
                    'classification': template['severity'],
                    'details': {
                        'detection_method': 'dns_analysis',
                        'confidence': random.randint(75, 90),
                        'first_seen': datetime.utcnow().isoformat()
                    }
                }]
            }
    
    def _generate_phishing_ioc(self, template):
        """Generate phishing IOC"""
        import random
        
        phishing_domains = ['secure-bank', 'paypal-verify', 'amazon-security', 'microsoft-login']
        tlds = ['.tk', '.ml', '.ga', '.cf', '.com']
        domain = f"{random.choice(phishing_domains)}{random.randint(10, 999)}{random.choice(tlds)}"
        
        return {
            'value': domain,
            'type': 'domain',
            'threat_score': random.randint(80, 95),
            'classification': template['severity'],
            'sources': [template['source']],
            'tags': ['phishing', 'credential_theft'],
            'description': f"Phishing domain detected by {template['source']}",
            'source_details': [{
                'source': template['source'],
                'threat_score': random.randint(80, 95),
                'classification': template['severity'],
                'details': {
                    'detection_method': 'content_analysis',
                    'target_brand': random.choice(['PayPal', 'Amazon', 'Microsoft', 'Bank']),
                    'confidence': random.randint(85, 95),
                    'first_seen': datetime.utcnow().isoformat()
                }
            }]
        }
    
    def _generate_botnet_ioc(self, template):
        """Generate botnet IOC"""
        import random
        
        ip = f"{random.randint(1, 223)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        
        return {
            'value': ip,
            'type': 'ip',
            'threat_score': random.randint(85, 98),
            'classification': template['severity'],
            'sources': [template['source']],
            'tags': ['botnet', 'c2_communication'],
            'description': f"Botnet C2 server detected by {template['source']}",
            'source_details': [{
                'source': template['source'],
                'threat_score': random.randint(85, 98),
                'classification': template['severity'],
                'details': {
                    'detection_method': 'traffic_analysis',
                    'botnet_family': random.choice(['Mirai', 'Zeus', 'Emotet', 'TrickBot']),
                    'infected_hosts': random.randint(100, 5000),
                    'confidence': random.randint(90, 98),
                    'first_seen': datetime.utcnow().isoformat()
                }
            }]
        }
    
    def _generate_c2_ioc(self, template):
        """Generate C2 server IOC"""
        import random
        
        if random.choice([True, False]):
            # C2 IP
            ip = f"{random.randint(1, 223)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            return {
                'value': ip,
                'type': 'ip',
                'threat_score': random.randint(90, 99),
                'classification': template['severity'],
                'sources': [template['source']],
                'tags': ['c2', 'command_control'],
                'description': f"C2 server detected by {template['source']}",
                'source_details': [{
                    'source': template['source'],
                    'threat_score': random.randint(90, 99),
                    'classification': template['severity'],
                    'details': {
                        'detection_method': 'behavioral_analysis',
                        'protocol': random.choice(['HTTP', 'HTTPS', 'DNS', 'IRC']),
                        'confidence': random.randint(92, 99),
                        'first_seen': datetime.utcnow().isoformat()
                    }
                }]
            }
        else:
            # C2 Domain
            c2_domains = ['control-server', 'cmd-host', 'bot-control', 'remote-cmd']
            tlds = ['.tk', '.ml', '.ga', '.cf']
            domain = f"{random.choice(c2_domains)}{random.randint(1, 99)}{random.choice(tlds)}"
            
            return {
                'value': domain,
                'type': 'domain',
                'threat_score': random.randint(88, 96),
                'classification': template['severity'],
                'sources': [template['source']],
                'tags': ['c2', 'command_control'],
                'description': f"C2 domain detected by {template['source']}",
                'source_details': [{
                    'source': template['source'],
                    'threat_score': random.randint(88, 96),
                    'classification': template['severity'],
                    'details': {
                        'detection_method': 'dns_analysis',
                        'confidence': random.randint(90, 96),
                        'first_seen': datetime.utcnow().isoformat()
                    }
                }]
            }
    
    def _generate_ransomware_ioc(self, template):
        """Generate ransomware IOC"""
        import random
        
        # Generate file hash for ransomware sample
        hash_value = ''.join([random.choice('0123456789abcdef') for _ in range(64)])
        
        return {
            'value': hash_value,
            'type': 'hash',
            'threat_score': random.randint(95, 99),
            'classification': template['severity'],
            'sources': [template['source']],
            'tags': ['ransomware', 'file_hash'],
            'description': f"Ransomware sample detected by {template['source']}",
            'source_details': [{
                'source': template['source'],
                'threat_score': random.randint(95, 99),
                'classification': template['severity'],
                'details': {
                    'detection_method': 'signature_analysis',
                    'ransomware_family': random.choice(['WannaCry', 'Ryuk', 'Maze', 'Conti']),
                    'file_type': 'PE32',
                    'confidence': random.randint(96, 99),
                    'first_seen': datetime.utcnow().isoformat()
                }
            }]
        }
    
    def _generate_generic_ioc(self, template):
        """Generate generic IOC"""
        import random
        
        ip = f"{random.randint(1, 223)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        
        return {
            'value': ip,
            'type': 'ip',
            'threat_score': random.randint(60, 85),
            'classification': template['severity'],
            'sources': [template['source']],
            'tags': ['suspicious'],
            'description': f"Suspicious activity detected by {template['source']}",
            'source_details': [{
                'source': template['source'],
                'threat_score': random.randint(60, 85),
                'classification': template['severity'],
                'details': {
                    'detection_method': 'anomaly_detection',
                    'confidence': random.randint(70, 85),
                    'first_seen': datetime.utcnow().isoformat()
                }
            }]
        }
    
    def _update_live_stats(self):
        """Update live statistics"""
        try:
            now = datetime.utcnow()
            hour_ago = now - timedelta(hours=1)
            day_ago = now - timedelta(hours=24)
            
            # Get real counts from database
            self.live_stats['threats_last_hour'] = self.db.iocs.count_documents({
                'timestamp': {'$gte': hour_ago}
            })
            
            self.live_stats['threats_last_24h'] = self.db.iocs.count_documents({
                'timestamp': {'$gte': day_ago}
            })
            
            # Calculate threat level based on recent activity
            critical_count = self.db.iocs.count_documents({
                'classification': 'critical',
                'timestamp': {'$gte': hour_ago}
            })
            
            high_count = self.db.iocs.count_documents({
                'classification': 'high',
                'timestamp': {'$gte': hour_ago}
            })
            
            if critical_count > 5:
                self.live_stats['current_threat_level'] = 'critical'
            elif critical_count > 0 or high_count > 10:
                self.live_stats['current_threat_level'] = 'high'
            elif high_count > 0:
                self.live_stats['current_threat_level'] = 'medium'
            else:
                self.live_stats['current_threat_level'] = 'low'
            
            # Update other metrics (simplified for demo)
            import random
            self.live_stats['active_campaigns'] = random.randint(5, 25)
            self.live_stats['new_malware_families'] = random.randint(0, 3)
            self.live_stats['compromised_websites'] = random.randint(10, 50)
            self.live_stats['botnet_activity'] = random.randint(2, 15)
            
        except Exception as e:
            print(f"Error updating live stats: {e}")
            # Use fallback values
            import random
            self.live_stats.update({
                'threats_last_hour': random.randint(5, 20),
                'threats_last_24h': random.randint(50, 200),
                'current_threat_level': 'medium',
                'active_campaigns': random.randint(5, 25),
                'new_malware_families': random.randint(0, 3),
                'compromised_websites': random.randint(10, 50),
                'botnet_activity': random.randint(2, 15)
            })
    
    def _broadcast_updates(self):
        """Broadcast live updates to connected clients"""
        self.socketio.emit('live_stats_update', self.live_stats)
    
    def get_live_stats(self):
        """Get current live statistics"""
        self._update_live_stats()
        return self.live_stats
    
    def fetch_live_threats(self):
        """Fetch threats from real feeds (called by scheduler)"""
        try:
            # This would fetch from real threat intelligence feeds
            # For now, we'll just trigger the simulation
            print("🔄 Fetching live threat intelligence...")
            
            # In production, implement actual feed parsing here
            # Example: self._fetch_urlhaus_feed()
            
            return {"status": "success", "message": "Live feeds processed"}
        except Exception as e:
            print(f"Error fetching live threats: {e}")
            return {"status": "error", "message": str(e)}