from pymongo import MongoClient
from datetime import datetime, timedelta
import os
import json
import csv
from io import StringIO

class DatabaseService:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        self.db = self.client[os.getenv('DATABASE_NAME', 'cti_dashboard')]
        self.iocs = self.db.iocs
        self.feeds = self.db.feeds
        
        # Create indexes for better performance
        self.iocs.create_index([("value", 1), ("type", 1)])
        self.iocs.create_index("timestamp")
        self.iocs.create_index("tags")
    
    def store_ioc(self, ioc_data):
        """Store IOC with deduplication"""
        existing = self.iocs.find_one({
            "value": ioc_data["value"],
            "type": ioc_data["type"]
        })
        
        if existing:
            # Update existing IOC with new data
            update_data = {
                "last_seen": datetime.utcnow(),
                "sources": list(set(existing.get("sources", []) + ioc_data.get("sources", []))),
                "threat_score": max(existing.get("threat_score", 0), ioc_data.get("threat_score", 0))
            }
            self.iocs.update_one({"_id": existing["_id"]}, {"$set": update_data})
            return existing["_id"]
        else:
            # Insert new IOC
            ioc_data["timestamp"] = datetime.utcnow()
            ioc_data["last_seen"] = datetime.utcnow()
            ioc_data["tags"] = ioc_data.get("tags", [])
            result = self.iocs.insert_one(ioc_data)
            return result.inserted_id
    
    def get_ioc(self, value, ioc_type):
        """Get IOC by value and type"""
        return self.iocs.find_one({"value": value, "type": ioc_type})
    
    def get_iocs_paginated(self, page=1, limit=50, search="", tag_filter=""):
        """Get paginated IOCs with search and filtering"""
        query = {}
        
        if search:
            query["$or"] = [
                {"value": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        if tag_filter:
            query["tags"] = tag_filter
        
        skip = (page - 1) * limit
        total = self.iocs.count_documents(query)
        
        iocs = list(self.iocs.find(query)
                   .sort("timestamp", -1)
                   .skip(skip)
                   .limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for ioc in iocs:
            ioc["_id"] = str(ioc["_id"])
        
        return {
            "iocs": iocs,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
    
    def update_ioc_tags(self, ioc_id, tags):
        """Update IOC tags"""
        from bson import ObjectId
        result = self.iocs.update_one(
            {"_id": ObjectId(ioc_id)},
            {"$set": {"tags": tags}}
        )
        return result.modified_count > 0
    
    def get_threat_stats(self):
        """Get threat statistics for dashboard"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$classification",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            stats = list(self.iocs.aggregate(pipeline))
            
            # Get recent IOCs count (last 24 hours)
            recent_count = self.iocs.count_documents({
                "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=24)}
            })
            
            # Get top malicious IPs/domains (use different classification values)
            top_malicious = list(self.iocs.find({
                "$or": [
                    {"classification": "critical"},
                    {"classification": "high"},
                    {"classification": "malicious"}
                ]
            }).sort("threat_score", -1).limit(10))
            
            return {
                "classification_stats": stats,
                "recent_count": recent_count,
                "top_malicious": top_malicious,
                "total_iocs": self.iocs.count_documents({})
            }
        except Exception as e:
            print(f"Error getting threat stats: {e}")
            return {
                "classification_stats": [],
                "recent_count": 0,
                "top_malicious": [],
                "total_iocs": 0
            }
    
    def get_trends_data(self, days=7):
        """Get trend data for specified number of days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                        "classification": "$classification"
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.date": 1}}
        ]
        
        return list(self.iocs.aggregate(pipeline))
    
    def export_iocs(self, days=30, format_type="json"):
        """Export IOCs in specified format"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        iocs = list(self.iocs.find(
            {"timestamp": {"$gte": start_date}}
        ).sort("timestamp", -1))
        
        # Convert ObjectId to string
        for ioc in iocs:
            ioc["_id"] = str(ioc["_id"])
            ioc["timestamp"] = ioc["timestamp"].isoformat()
            ioc["last_seen"] = ioc["last_seen"].isoformat()
        
        if format_type == "csv":
            output = StringIO()
            if iocs:
                fieldnames = iocs[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(iocs)
            return output.getvalue()
        else:
            return json.dumps(iocs, indent=2)
    
    def store_feed_data(self, feed_name, data):
        """Store feed data with timestamp"""
        feed_doc = {
            "name": feed_name,
            "data": data,
            "timestamp": datetime.utcnow()
        }
        return self.feeds.insert_one(feed_doc)    

    def get_ip_threat_timeline(self, ip_address):
        """Get threat timeline for a specific IP"""
        try:
            # Get all IOCs for this IP
            iocs = list(self.iocs.find({"value": ip_address, "type": "ip"}).sort("timestamp", -1))
            
            timeline = []
            for ioc in iocs:
                timeline.append({
                    "timestamp": ioc.get("timestamp", datetime.utcnow()).isoformat(),
                    "event": f"Threat Detection - {ioc.get('classification', 'unknown').title()}",
                    "description": ioc.get("description", "Malicious activity detected"),
                    "severity": ioc.get("classification", "medium"),
                    "source": ioc.get("sources", ["unknown"])[0] if ioc.get("sources") else "unknown",
                    "threat_score": ioc.get("threat_score", 0)
                })
            
            return timeline
        except Exception as e:
            print(f"Error getting IP timeline: {e}")
            return []