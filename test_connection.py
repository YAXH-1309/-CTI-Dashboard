#!/usr/bin/env python3
"""
Test database connection and basic functionality
"""

import os
import sys
from dotenv import load_dotenv

def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        from services.database import DatabaseService
        
        print("Testing MongoDB connection...")
        db_service = DatabaseService()
        
        # Test basic operations
        test_ioc = {
            'value': '192.168.1.100',
            'type': 'ip',
            'threat_score': 75,
            'classification': 'high',
            'sources': ['test'],
            'tags': ['test', 'malware'],
            'description': 'Test IOC for connection verification'
        }
        
        # Store test IOC
        ioc_id = db_service.store_ioc(test_ioc)
        print(f"✓ Successfully stored test IOC: {ioc_id}")
        
        # Get threat stats
        stats = db_service.get_threat_stats()
        print(f"✓ Retrieved threat stats: {stats['total_iocs']} total IOCs")
        
        # Test visualization service
        from services.visualization import VisualizationService
        viz_service = VisualizationService(db_service)
        
        dashboard_data = viz_service.get_dashboard_metrics()
        print(f"✓ Dashboard metrics loaded successfully")
        
        print("\n🎉 All database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_realtime_service():
    """Test real-time service"""
    try:
        from services.database import DatabaseService
        from services.realtime_feeds import RealtimeFeedService
        
        print("\nTesting real-time service...")
        
        # Mock socketio for testing
        class MockSocketIO:
            def emit(self, event, data):
                print(f"Mock emit: {event} - {type(data)}")
        
        db_service = DatabaseService()
        realtime_service = RealtimeFeedService(db_service, MockSocketIO())
        
        # Test live stats
        stats = realtime_service.get_live_stats()
        print(f"✓ Live stats retrieved: {stats['current_threat_level']} threat level")
        
        print("✓ Real-time service test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Real-time service test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 CTI Dashboard - Connection Tests")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Run tests
    tests_passed = 0
    total_tests = 2
    
    if test_mongodb_connection():
        tests_passed += 1
    
    if test_realtime_service():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The dashboard should work correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)