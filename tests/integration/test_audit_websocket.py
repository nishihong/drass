#!/usr/bin/env python3
"""
Test script for Audit WebSocket functionality
"""

import asyncio
import json
import sys
import os
import websockets
import httpx
from datetime import datetime

# Add the services directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'main-app'))

from app.services.audit_service import (
    audit_service,
    AuditEventType,
    AuditSeverity,
    AuditStatus
)


async def test_websocket_connection():
    """Test WebSocket connection and message handling"""
    
    print("🧪 Testing Audit WebSocket Connection...")
    print("=" * 50)
    
    user_id = "test_user_websocket"
    ws_url = f"ws://localhost:8888/api/v1/ws/audit/{user_id}"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"✅ Connected to WebSocket: {ws_url}")
            
            # Test 1: Receive welcome message
            print("\n1. Testing welcome message...")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"✅ Received welcome message: {data.get('type', 'unknown')}")
                print(f"   - Message: {data.get('message', 'N/A')}")
                print(f"   - User ID: {data.get('user_id', 'N/A')}")
            except asyncio.TimeoutError:
                print("❌ Timeout waiting for welcome message")
            except Exception as e:
                print(f"❌ Error receiving welcome message: {e}")
            
            # Test 2: Send ping message
            print("\n2. Testing ping/pong...")
            try:
                ping_message = {"type": "ping"}
                await websocket.send(json.dumps(ping_message))
                print("✅ Sent ping message")
                
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                if data.get("type") == "pong":
                    print("✅ Received pong response")
                else:
                    print(f"❌ Unexpected response: {data}")
            except asyncio.TimeoutError:
                print("❌ Timeout waiting for pong response")
            except Exception as e:
                print(f"❌ Error in ping/pong test: {e}")
            
            # Test 3: Get connection stats
            print("\n3. Testing connection stats...")
            try:
                stats_message = {"type": "get_stats"}
                await websocket.send(json.dumps(stats_message))
                print("✅ Sent stats request")
                
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                if data.get("type") == "connection_stats":
                    stats = data.get("stats", {})
                    print("✅ Received connection stats:")
                    print(f"   - Total connections: {stats.get('total_connections', 'N/A')}")
                    print(f"   - Total users: {stats.get('total_users', 'N/A')}")
                    print(f"   - Total messages: {stats.get('total_messages_sent', 'N/A')}")
                else:
                    print(f"❌ Unexpected response: {data}")
            except asyncio.TimeoutError:
                print("❌ Timeout waiting for stats response")
            except Exception as e:
                print(f"❌ Error in stats test: {e}")
            
            # Test 4: Subscribe to events
            print("\n4. Testing event subscription...")
            try:
                subscribe_message = {
                    "type": "subscribe",
                    "event_types": ["user_login", "document_upload", "compliance_analysis"]
                }
                await websocket.send(json.dumps(subscribe_message))
                print("✅ Sent subscription request")
                
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                if data.get("type") == "subscription_confirmed":
                    print("✅ Subscription confirmed")
                    print(f"   - Event types: {data.get('event_types', [])}")
                else:
                    print(f"❌ Unexpected response: {data}")
            except asyncio.TimeoutError:
                print("❌ Timeout waiting for subscription response")
            except Exception as e:
                print(f"❌ Error in subscription test: {e}")
            
            # Test 5: Wait for audit events (with timeout)
            print("\n5. Testing audit event reception...")
            try:
                # Log an audit event to trigger WebSocket broadcast
                print("   Logging test audit event...")
                await audit_service.log_audit_event(
                    event_type=AuditEventType.USER_LOGIN,
                    user_id=user_id,
                    details={
                        "login_method": "websocket_test",
                        "test": True
                    },
                    resource_type="authentication",
                    action="login",
                    severity=AuditSeverity.MEDIUM,
                    status=AuditStatus.SUCCESS
                )
                print("   ✅ Audit event logged")
                
                # Wait for the event to be broadcast
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                if data.get("type") == "audit_event":
                    print("✅ Received audit event via WebSocket:")
                    print(f"   - Event ID: {data.get('event_id', 'N/A')}")
                    print(f"   - Event Type: {data.get('event_type', 'N/A')}")
                    print(f"   - User ID: {data.get('user_id', 'N/A')}")
                    print(f"   - Severity: {data.get('severity', 'N/A')}")
                    print(f"   - Status: {data.get('status', 'N/A')}")
                else:
                    print(f"❌ Unexpected message type: {data.get('type', 'unknown')}")
            except asyncio.TimeoutError:
                print("❌ Timeout waiting for audit event")
            except Exception as e:
                print(f"❌ Error in audit event test: {e}")
            
            print("\n✅ WebSocket connection test completed")
            
    except websockets.exceptions.ConnectionClosed:
        print("❌ WebSocket connection closed unexpectedly")
    except websockets.exceptions.InvalidURI:
        print("❌ Invalid WebSocket URI")
    except Exception as e:
        print(f"❌ Error connecting to WebSocket: {e}")


async def test_websocket_api_endpoints():
    """Test WebSocket-related API endpoints"""
    
    print("\n🌐 Testing WebSocket API endpoints...")
    print("=" * 50)
    
    base_url = "http://localhost:8888/api/v1"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test WebSocket stats endpoint
            print("\n1. Testing WebSocket stats endpoint...")
            response = await client.get(f"{base_url}/ws/audit/stats")
            if response.status_code == 200:
                stats = response.json()
                print("✅ WebSocket stats retrieved:")
                print(f"   - Total connections: {stats.get('total_connections', 'N/A')}")
                print(f"   - Total users: {stats.get('total_users', 'N/A')}")
                print(f"   - Total messages: {stats.get('total_messages_sent', 'N/A')}")
            else:
                print(f"❌ WebSocket stats failed: {response.status_code}")
            
            # Test WebSocket health endpoint
            print("\n2. Testing WebSocket health endpoint...")
            response = await client.get(f"{base_url}/ws/audit/health")
            if response.status_code == 200:
                health = response.json()
                print(f"✅ WebSocket health: {health.get('status', 'unknown')}")
                print(f"   - Service: {health.get('service', 'N/A')}")
            else:
                print(f"❌ WebSocket health failed: {response.status_code}")
            
            # Test WebSocket test page
            print("\n3. Testing WebSocket test page...")
            response = await client.get(f"{base_url}/ws/audit/test")
            if response.status_code == 200:
                print("✅ WebSocket test page accessible")
                print(f"   - Content length: {len(response.text)} characters")
            else:
                print(f"❌ WebSocket test page failed: {response.status_code}")
                
    except httpx.ConnectError:
        print("❌ Cannot connect to API server. Make sure the server is running on port 8888")
    except Exception as e:
        print(f"❌ Error testing WebSocket API endpoints: {e}")


async def test_multiple_connections():
    """Test multiple WebSocket connections"""
    
    print("\n🔗 Testing multiple WebSocket connections...")
    print("=" * 50)
    
    user_ids = ["user1", "user2", "user3"]
    connections = []
    
    try:
        # Connect multiple users
        for user_id in user_ids:
            ws_url = f"ws://localhost:8888/api/v1/ws/audit/{user_id}"
            websocket = await websockets.connect(ws_url)
            connections.append((user_id, websocket))
            print(f"✅ Connected user: {user_id}")
        
        # Wait for all welcome messages
        print("\nWaiting for welcome messages...")
        for user_id, websocket in connections:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"✅ {user_id} received welcome: {data.get('type', 'unknown')}")
            except asyncio.TimeoutError:
                print(f"❌ {user_id} timeout waiting for welcome")
        
        # Log an audit event and see if all connections receive it
        print("\nLogging audit event for broadcast...")
        await audit_service.log_audit_event(
            event_type=AuditEventType.DOCUMENT_UPLOAD,
            user_id="broadcast_test_user",
            details={
                "filename": "test_multiple_connections.pdf",
                "test": True
            },
            resource_type="document",
            action="upload",
            severity=AuditSeverity.LOW,
            status=AuditStatus.SUCCESS
        )
        print("✅ Audit event logged")
        
        # Check if all connections receive the event
        print("\nChecking if all connections receive the event...")
        for user_id, websocket in connections:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                if data.get("type") == "audit_event":
                    print(f"✅ {user_id} received audit event: {data.get('event_type', 'unknown')}")
                else:
                    print(f"❌ {user_id} received unexpected message: {data.get('type', 'unknown')}")
            except asyncio.TimeoutError:
                print(f"❌ {user_id} timeout waiting for audit event")
        
        # Close all connections
        print("\nClosing connections...")
        for user_id, websocket in connections:
            await websocket.close()
            print(f"✅ Closed connection for {user_id}")
        
    except Exception as e:
        print(f"❌ Error in multiple connections test: {e}")
        # Ensure all connections are closed
        for user_id, websocket in connections:
            try:
                await websocket.close()
            except:
                pass


async def main():
    """Main test function"""
    print("🚀 Starting Audit WebSocket Tests")
    print("=" * 60)
    
    # Test WebSocket connection
    await test_websocket_connection()
    
    # Test API endpoints
    await test_websocket_api_endpoints()
    
    # Test multiple connections
    await test_multiple_connections()
    
    print("\n" + "=" * 60)
    print("✨ All WebSocket tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
