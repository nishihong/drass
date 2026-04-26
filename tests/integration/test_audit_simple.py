#!/usr/bin/env python3
"""
Simple test for enhanced audit logging system
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'main-app'))

async def test_audit_service():
    """Test the enhanced audit service"""
    try:
        from app.services.audit_service_enhanced import audit_service_enhanced, AuditEventType, AuditSeverity, AuditStatus
        
        print("Testing enhanced audit service...")
        
        # Test health check
        print("1. Testing health check...")
        health = await audit_service_enhanced.health_check()
        print(f"   Health status: {health.get('status')}")
        print(f"   Database connected: {health.get('database_connected')}")
        print(f"   Storage type: {health.get('storage_type')}")
        
        # Test logging an event
        print("2. Testing audit event logging...")
        audit_entry = await audit_service_enhanced.log_audit_event(
            event_type=AuditEventType.API_ACCESS,
            user_id="test_user_123",
            details={"test": True, "operation": "simple_test"},
            action="test_action",
            severity=AuditSeverity.MEDIUM,
            status=AuditStatus.SUCCESS,
            ip_address="127.0.0.1",
            user_agent="SimpleTest/1.0"
        )
        print(f"   Logged event ID: {audit_entry.id}")
        print(f"   Event type: {audit_entry.event_type.value}")
        print(f"   User ID: {audit_entry.user_id}")
        
        # Test querying logs
        print("3. Testing audit log query...")
        logs = await audit_service_enhanced.get_audit_logs(limit=10)
        print(f"   Found {len(logs)} audit logs")
        if logs:
            latest_log = logs[0]
            print(f"   Latest log: {latest_log.event_type.value} by {latest_log.user_id}")
        
        # Test statistics
        print("4. Testing audit statistics...")
        stats = await audit_service_enhanced.get_audit_statistics()
        print(f"   Total events: {stats.get('total_events', 0)}")
        print(f"   Success rate: {stats.get('success_rate', 0):.1f}%")
        
        print("\n✅ All tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_audit_service())
