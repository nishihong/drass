#!/usr/bin/env python3
"""
Test script for AuditService
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta

# Add the services directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'main-app'))

from app.services.audit_service import (
    audit_service,
    AuditEventType,
    AuditSeverity,
    AuditStatus
)


async def test_audit_service():
    """Test the AuditService functionality"""
    
    print("🧪 Testing AuditService...")
    print("=" * 50)
    
    # Test 1: Log audit events
    print("\n1. Testing audit event logging...")
    try:
        # Log a user login event
        login_event = await audit_service.log_audit_event(
            event_type=AuditEventType.USER_LOGIN,
            user_id="user123",
            details={
                "login_method": "password",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0"
            },
            resource_type="authentication",
            action="login",
            severity=AuditSeverity.MEDIUM,
            status=AuditStatus.SUCCESS,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            session_id="session123"
        )
        print(f"✅ Logged login event: {login_event.id}")
        
        # Log a document upload event
        upload_event = await audit_service.log_audit_event(
            event_type=AuditEventType.DOCUMENT_UPLOAD,
            user_id="user123",
            details={
                "filename": "test_document.pdf",
                "file_size": 1024000,
                "file_type": "application/pdf"
            },
            resource_type="document",
            resource_id="doc456",
            action="upload",
            severity=AuditSeverity.LOW,
            status=AuditStatus.SUCCESS,
            ip_address="192.168.1.100"
        )
        print(f"✅ Logged upload event: {upload_event.id}")
        
        # Log a compliance analysis event
        analysis_event = await audit_service.log_audit_event(
            event_type=AuditEventType.COMPLIANCE_ANALYSIS,
            user_id="user123",
            details={
                "analysis_type": "data_classification",
                "data_sensitivity": "high",
                "compliance_standards": ["GDPR", "SOC2"]
            },
            resource_type="compliance",
            action="analyze",
            severity=AuditSeverity.HIGH,
            status=AuditStatus.SUCCESS
        )
        print(f"✅ Logged analysis event: {analysis_event.id}")
        
        # Log an error event
        error_event = await audit_service.log_audit_event(
            event_type=AuditEventType.ERROR_EVENT,
            user_id="user123",
            details={
                "error_type": "validation_error",
                "error_code": "INVALID_FORMAT"
            },
            resource_type="system",
            action="validate",
            severity=AuditSeverity.MEDIUM,
            status=AuditStatus.FAILURE,
            error_message="Invalid document format"
        )
        print(f"✅ Logged error event: {error_event.id}")
        
    except Exception as e:
        print(f"❌ Error logging audit events: {e}")
    
    # Test 2: Get audit logs
    print("\n2. Testing audit log retrieval...")
    try:
        # Get all logs
        all_logs = await audit_service.get_audit_logs(limit=10)
        print(f"✅ Retrieved {len(all_logs)} audit logs")
        
        # Get logs by user
        user_logs = await audit_service.get_audit_logs(user_id="user123", limit=5)
        print(f"✅ Retrieved {len(user_logs)} logs for user123")
        
        # Get logs by event type
        login_logs = await audit_service.get_audit_logs(
            event_type=AuditEventType.USER_LOGIN,
            limit=5
        )
        print(f"✅ Retrieved {len(login_logs)} login events")
        
        # Get logs by severity
        high_severity_logs = await audit_service.get_audit_logs(
            severity=AuditSeverity.HIGH,
            limit=5
        )
        print(f"✅ Retrieved {len(high_severity_logs)} high severity events")
        
        # Get logs by status
        success_logs = await audit_service.get_audit_logs(
            status=AuditStatus.SUCCESS,
            limit=5
        )
        print(f"✅ Retrieved {len(success_logs)} successful events")
        
    except Exception as e:
        print(f"❌ Error getting audit logs: {e}")
    
    # Test 3: Search audit logs
    print("\n3. Testing audit log search...")
    try:
        # Search by text
        search_results = await audit_service.search_audit_logs("login", limit=5)
        print(f"✅ Found {len(search_results)} logs matching 'login'")
        
        # Search by user ID
        user_search = await audit_service.search_audit_logs("user123", limit=5)
        print(f"✅ Found {len(user_search)} logs matching 'user123'")
        
        # Search by error
        error_search = await audit_service.search_audit_logs("error", limit=5)
        print(f"✅ Found {len(error_search)} logs matching 'error'")
        
    except Exception as e:
        print(f"❌ Error searching audit logs: {e}")
    
    # Test 4: Get audit statistics
    print("\n4. Testing audit statistics...")
    try:
        # Get overall statistics
        stats = await audit_service.get_audit_statistics()
        print(f"✅ Retrieved audit statistics:")
        print(f"   - Total events: {stats['total_events']}")
        print(f"   - Success events: {stats['success_events']}")
        print(f"   - Failure events: {stats['failure_events']}")
        print(f"   - Success rate: {stats['success_rate']:.1f}%")
        print(f"   - Event types: {len(stats['event_type_counts'])}")
        print(f"   - Severity levels: {len(stats['severity_counts'])}")
        
        # Get statistics for last 24 hours
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        recent_stats = await audit_service.get_audit_statistics(
            start_date=start_date,
            end_date=end_date
        )
        print(f"✅ Retrieved recent statistics: {recent_stats['total_events']} events in last 24h")
        
    except Exception as e:
        print(f"❌ Error getting audit statistics: {e}")
    
    # Test 5: Health check
    print("\n5. Testing health check...")
    try:
        health = await audit_service.health_check()
        print(f"✅ Health check: {health['status']}")
        print(f"   - Total logs: {health['total_logs']}")
        print(f"   - Storage path: {health['storage_path']}")
        print(f"   - Broadcasters: {health['broadcasters']}")
        
    except Exception as e:
        print(f"❌ Error in health check: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 AuditService testing completed!")


async def test_api_endpoints():
    """Test the API endpoints"""
    
    print("\n🌐 Testing Audit API endpoints...")
    print("=" * 50)
    
    import httpx
    
    base_url = "http://localhost:8888/api/v1/audit"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            print("\n1. Testing health endpoint...")
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed: {health_data['status']}")
                print(f"   - Total logs: {health_data['total_logs']}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
            
            # Test logging an event
            print("\n2. Testing event logging...")
            event_data = {
                "event_type": "user_login",
                "user_id": "test_user",
                "details": {
                    "login_method": "password",
                    "ip_address": "192.168.1.100"
                },
                "resource_type": "authentication",
                "action": "login",
                "severity": "medium",
                "status": "success",
                "ip_address": "192.168.1.100"
            }
            response = await client.post(f"{base_url}/log", json=event_data)
            if response.status_code == 200:
                log_data = response.json()
                print(f"✅ Event logged: {log_data['id']}")
                print(f"   - Event type: {log_data['event_type']}")
                print(f"   - User: {log_data['user_id']}")
                print(f"   - Status: {log_data['status']}")
            else:
                print(f"❌ Event logging failed: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test getting logs
            print("\n3. Testing log retrieval...")
            response = await client.get(f"{base_url}/logs?limit=5")
            if response.status_code == 200:
                logs = response.json()
                print(f"✅ Retrieved {len(logs)} audit logs via API")
                if logs:
                    latest_log = logs[0]
                    print(f"   - Latest log: {latest_log['event_type']} by {latest_log['user_id']}")
            else:
                print(f"❌ Log retrieval failed: {response.status_code}")
            
            # Test search
            print("\n4. Testing log search...")
            response = await client.get(f"{base_url}/search?query=login&limit=5")
            if response.status_code == 200:
                search_results = response.json()
                print(f"✅ Found {len(search_results)} logs matching 'login'")
            else:
                print(f"❌ Log search failed: {response.status_code}")
            
            # Test statistics
            print("\n5. Testing statistics...")
            response = await client.get(f"{base_url}/statistics")
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Retrieved statistics:")
                print(f"   - Total events: {stats['total_events']}")
                print(f"   - Success rate: {stats['success_rate']:.1f}%")
            else:
                print(f"❌ Statistics failed: {response.status_code}")
            
            # Test available options
            print("\n6. Testing available options...")
            for endpoint in ["/event-types", "/severity-levels", "/status-types"]:
                response = await client.get(f"{base_url}{endpoint}")
                if response.status_code == 200:
                    options = response.json()
                    print(f"✅ {endpoint}: {len(options)} options")
                else:
                    print(f"❌ {endpoint} failed: {response.status_code}")
                
    except httpx.ConnectError:
        print("❌ Cannot connect to API server. Make sure the server is running on port 8888")
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")


async def main():
    """Main test function"""
    print("🚀 Starting AuditService Tests")
    print("=" * 60)
    
    # Test service directly
    await test_audit_service()
    
    # Test API endpoints
    await test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("✨ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
