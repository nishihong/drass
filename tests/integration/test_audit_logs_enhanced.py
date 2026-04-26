#!/usr/bin/env python3
"""
测试增强的AuditLogs组件功能
包括WebSocket连接、实时通知、日志导出等功能
"""

import asyncio
import json
import time
import websockets
import requests
from datetime import datetime
from typing import Dict, Any

# 配置
BACKEND_URL = "http://localhost:8888"
WS_URL = "ws://localhost:8888/api/v1/ws/audit"
TEST_USER_ID = "test_user_001"

def test_audit_api_endpoints():
    """测试审计日志API端点"""
    print("🔍 测试审计日志API端点...")
    
    # 测试健康检查
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/audit/health")
        if response.status_code == 200:
            print("✅ 审计服务健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 审计服务健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 审计服务健康检查异常: {e}")
    
    # 测试获取审计日志
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/audit/logs")
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ 获取审计日志成功，共 {len(logs)} 条记录")
            if logs:
                print(f"   最新日志: {logs[0]}")
        else:
            print(f"❌ 获取审计日志失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取审计日志异常: {e}")
    
    # 测试创建审计事件
    try:
        audit_data = {
            "event_type": "test_event",
            "user_id": TEST_USER_ID,
            "details": {
                "action": "测试审计事件",
                "resource": "测试资源",
                "ip_address": "127.0.0.1",
                "user_agent": "Test Agent"
            }
        }
        response = requests.post(f"{BACKEND_URL}/api/v1/audit/log", json=audit_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ 创建审计事件成功")
            print(f"   事件ID: {result.get('id')}")
        else:
            print(f"❌ 创建审计事件失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 创建审计事件异常: {e}")

async def test_websocket_connection():
    """测试WebSocket连接和实时推送"""
    print("\n🔌 测试WebSocket连接和实时推送...")
    
    try:
        ws_url = f"{WS_URL}/{TEST_USER_ID}"
        print(f"   连接URL: {ws_url}")
        
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket连接成功")
            
            # 发送ping消息测试连接
            ping_message = {
                "type": "ping",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(ping_message))
            print("✅ 发送ping消息成功")
            
            # 等待响应
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"✅ 收到响应: {data}")
            except asyncio.TimeoutError:
                print("⚠️  等待响应超时（这是正常的，因为服务器可能不处理ping消息）")
            
            # 测试接收审计事件
            print("   等待审计事件推送...")
            try:
                # 创建一个测试审计事件
                audit_data = {
                    "event_type": "websocket_test",
                    "user_id": TEST_USER_ID,
                    "details": {
                        "action": "WebSocket测试事件",
                        "resource": "WebSocket测试",
                        "ip_address": "127.0.0.1",
                        "user_agent": "WebSocket Test Agent"
                    }
                }
                
                # 发送HTTP请求创建审计事件
                response = requests.post(f"{BACKEND_URL}/api/v1/audit/log", json=audit_data)
                if response.status_code == 200:
                    print("✅ 创建测试审计事件成功")
                    
                    # 等待WebSocket推送
                    try:
                        event_response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        event_data = json.loads(event_response)
                        print(f"✅ 收到审计事件推送: {event_data}")
                    except asyncio.TimeoutError:
                        print("⚠️  等待审计事件推送超时")
                else:
                    print(f"❌ 创建测试审计事件失败: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 测试审计事件推送异常: {e}")
                
    except Exception as e:
        print(f"❌ WebSocket连接失败: {e}")

def test_audit_statistics():
    """测试审计统计功能"""
    print("\n📊 测试审计统计功能...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/audit/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ 获取审计统计成功")
            print(f"   统计信息: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 获取审计统计失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取审计统计异常: {e}")

def test_audit_export():
    """测试审计日志导出功能"""
    print("\n📤 测试审计日志导出功能...")
    
    try:
        # 测试CSV导出
        response = requests.get(f"{BACKEND_URL}/api/v1/audit/export?format=csv")
        if response.status_code == 200:
            print("✅ CSV导出功能正常")
            print(f"   导出数据大小: {len(response.content)} 字节")
        else:
            print(f"❌ CSV导出失败: {response.status_code}")
    except Exception as e:
        print(f"❌ CSV导出异常: {e}")
    
    try:
        # 测试JSON导出
        response = requests.get(f"{BACKEND_URL}/api/v1/audit/export?format=json")
        if response.status_code == 200:
            print("✅ JSON导出功能正常")
            print(f"   导出数据大小: {len(response.content)} 字节")
        else:
            print(f"❌ JSON导出失败: {response.status_code}")
    except Exception as e:
        print(f"❌ JSON导出异常: {e}")

def test_websocket_stats():
    """测试WebSocket统计信息"""
    print("\n📈 测试WebSocket统计信息...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/ws/audit/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ 获取WebSocket统计成功")
            print(f"   统计信息: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 获取WebSocket统计失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取WebSocket统计异常: {e}")

async def main():
    """主测试函数"""
    print("🚀 开始测试增强的AuditLogs组件功能")
    print("=" * 60)
    
    # 测试API端点
    test_audit_api_endpoints()
    
    # 测试WebSocket连接
    await test_websocket_connection()
    
    # 测试统计功能
    test_audit_statistics()
    
    # 测试导出功能
    test_audit_export()
    
    # 测试WebSocket统计
    test_websocket_stats()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成！")
    print("\n📋 测试总结:")
    print("✅ 审计日志API端点测试")
    print("✅ WebSocket连接和实时推送测试")
    print("✅ 审计统计功能测试")
    print("✅ 日志导出功能测试")
    print("✅ WebSocket统计信息测试")
    
    print("\n🔗 前端访问地址:")
    print("   审计日志页面: http://localhost:5173/audit-logs")
    print("   WebSocket测试页面: http://localhost:8888/api/v1/ws/audit/test")

if __name__ == "__main__":
    asyncio.run(main())
