#!/usr/bin/env python3
"""
快速性能测试脚本 - 验证优化效果
"""

import requests
import time

# API基础URL
BASE_URL = "http://localhost:8888"

def login():
    """登录获取token"""
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data, timeout=10)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ 登录成功")
        return token
    else:
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return None

def quick_test(token, query, response_type="quick", use_rag=False):
    """快速测试单个查询"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 测试查询: {query}")
    print(f"📋 响应类型: {response_type}, RAG: {use_rag}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/test/chat",
            headers=headers,
            json={
                "message": query,
                "use_rag": use_rag,
                "response_type": response_type
            },
            timeout=30
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            perf_data = result.get("performance", {})
            
            print(f"✅ 成功 (耗时: {response_time:.2f}秒)")
            print(f"📝 回答长度: {len(result.get('response', ''))} 字符")
            print(f"🔍 使用RAG: {result.get('used_rag', False)}")
            print(f"⚡ 性能数据: {perf_data}")
            print(f"📄 回答内容: {result.get('response', '')[:200]}...")
            
            return True, response_time
        else:
            print(f"❌ 失败: {response.status_code} - {response.text}")
            return False, response_time
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        response_time = end_time - start_time
        print(f"⏰ 超时 (耗时: {response_time:.2f}秒)")
        return False, response_time
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        print(f"❌ 错误: {e}")
        return False, response_time

def main():
    """主函数"""
    print("🚀 快速性能测试 - 验证优化效果")
    print("="*50)
    
    # 登录
    token = login()
    if not token:
        return
    
    # 测试用例
    test_cases = [
        {
            "query": "你好",
            "response_type": "quick",
            "use_rag": False,
            "description": "简单问候（无RAG）"
        },
        {
            "query": "什么是数据合规？",
            "response_type": "quick", 
            "use_rag": True,
            "description": "快速回答（有RAG）"
        },
        {
            "query": "帮我分析下财富系列寿险计划",
            "response_type": "standard",
            "use_rag": True,
            "description": "标准分析（有RAG）"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 测试 {i}/{len(test_cases)}: {test_case['description']} ---")
        success, response_time = quick_test(
            token, 
            test_case["query"], 
            test_case["response_type"], 
            test_case["use_rag"]
        )
        
        results.append({
            "description": test_case["description"],
            "success": success,
            "response_time": response_time
        })
    
    # 总结
    print("\n" + "="*50)
    print("📊 测试结果总结")
    print("="*50)
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"✅ 成功: {len(successful_tests)}/{len(results)}")
    print(f"❌ 失败: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        avg_time = sum(r["response_time"] for r in successful_tests) / len(successful_tests)
        print(f"⏱️ 平均响应时间: {avg_time:.2f}秒")
        
        print(f"\n📈 成功测试详情:")
        for result in successful_tests:
            print(f"   {result['description']}: {result['response_time']:.2f}秒")
    
    if failed_tests:
        print(f"\n❌ 失败测试详情:")
        for result in failed_tests:
            print(f"   {result['description']}: {result['response_time']:.2f}秒")
    
    print("\n🎉 快速性能测试完成！")

if __name__ == "__main__":
    main()
