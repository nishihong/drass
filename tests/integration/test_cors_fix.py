#!/usr/bin/env python3
"""
测试CORS修复是否成功
"""

import requests
import json

def test_cors_fix():
    """测试CORS修复"""
    print("🔍 测试CORS修复...")
    print("=" * 50)
    
    # 测试不同端口的CORS
    origins = [
        "http://localhost:5173",
        "http://localhost:5174"
    ]
    
    for origin in origins:
        print(f"\n📡 测试来源: {origin}")
        
        # 测试OPTIONS预检请求
        try:
            response = requests.options(
                "http://localhost:8888/api/v1/auth/login",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                },
                timeout=10
            )
            
            print(f"   OPTIONS请求状态: {response.status_code}")
            print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', '未设置')}")
            print(f"   Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', '未设置')}")
            print(f"   Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', '未设置')}")
            
        except Exception as e:
            print(f"   ❌ OPTIONS请求失败: {e}")
        
        # 测试实际登录请求
        try:
            response = requests.post(
                "http://localhost:8888/api/v1/auth/login",
                headers={
                    "Origin": origin,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data="username=test@example.com&password=testpassword123",
                timeout=10
            )
            
            print(f"   POST请求状态: {response.status_code}")
            print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', '未设置')}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 登录成功，获得token: {data.get('access_token', '')[:20]}...")
            else:
                print(f"   ❌ 登录失败: {response.text}")
                
        except Exception as e:
            print(f"   ❌ POST请求失败: {e}")
    
    print("\n🎯 测试结果总结:")
    print("   - 如果所有请求都返回正确的CORS头，说明修复成功")
    print("   - 如果仍然有CORS错误，需要进一步检查配置")

if __name__ == "__main__":
    test_cors_fix()
