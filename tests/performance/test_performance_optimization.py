#!/usr/bin/env python3
"""
VLLM性能优化测试脚本
"""

import requests
import time
import json
from typing import Dict, Any, List

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

def test_performance_optimization(token: str, test_cases: List[Dict[str, Any]]):
    """测试性能优化效果"""
    headers = {"Authorization": f"Bearer {token}"}
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 测试 {i}/{len(test_cases)}: {test_case['name']} ---")
        print(f"查询: {test_case['query']}")
        print(f"响应类型: {test_case['response_type']}")
        print(f"最大Token: {test_case['max_tokens']}")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/test/chat",
                headers=headers,
                json={
                    "message": test_case["query"],
                    "use_rag": test_case.get("use_rag", True),
                    "max_tokens": test_case["max_tokens"],
                    "response_type": test_case["response_type"]
                },
                timeout=test_case.get("timeout", 60)
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
                
                results.append({
                    "test_name": test_case["name"],
                    "response_time": response_time,
                    "success": True,
                    "response_length": len(result.get("response", "")),
                    "performance": perf_data
                })
            else:
                print(f"❌ 失败: {response.status_code} - {response.text}")
                results.append({
                    "test_name": test_case["name"],
                    "response_time": response_time,
                    "success": False,
                    "error": response.text
                })
                
        except requests.exceptions.Timeout:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"⏰ 超时 (耗时: {response_time:.2f}秒)")
            results.append({
                "test_name": test_case["name"],
                "response_time": response_time,
                "success": False,
                "error": "timeout"
            })
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"❌ 错误: {e}")
            results.append({
                "test_name": test_case["name"],
                "response_time": response_time,
                "success": False,
                "error": str(e)
            })
    
    return results

def analyze_results(results: List[Dict[str, Any]]):
    """分析测试结果"""
    print("\n" + "="*60)
    print("📊 性能测试结果分析")
    print("="*60)
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"✅ 成功测试: {len(successful_tests)}/{len(results)}")
    print(f"❌ 失败测试: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        avg_response_time = sum(r["response_time"] for r in successful_tests) / len(successful_tests)
        min_response_time = min(r["response_time"] for r in successful_tests)
        max_response_time = max(r["response_time"] for r in successful_tests)
        
        print(f"\n⏱️ 响应时间统计:")
        print(f"   平均响应时间: {avg_response_time:.2f}秒")
        print(f"   最快响应时间: {min_response_time:.2f}秒")
        print(f"   最慢响应时间: {max_response_time:.2f}秒")
        
        print(f"\n📈 详细结果:")
        for result in successful_tests:
            print(f"   {result['test_name']}: {result['response_time']:.2f}秒")
    
    if failed_tests:
        print(f"\n❌ 失败测试详情:")
        for result in failed_tests:
            print(f"   {result['test_name']}: {result.get('error', 'Unknown error')}")

def main():
    """主函数"""
    print("🚀 VLLM性能优化测试")
    print("="*60)
    
    # 登录
    token = login()
    if not token:
        return
    
    # 定义测试用例
    test_cases = [
        {
            "name": "快速回答测试",
            "query": "什么是数据合规？",
            "response_type": "quick",
            "max_tokens": 256,
            "use_rag": True,
            "timeout": 20
        },
        {
            "name": "标准回答测试",
            "query": "帮我分析下财富系列寿险计划，并给出报告",
            "response_type": "standard", 
            "max_tokens": 512,
            "use_rag": True,
            "timeout": 40
        },
        {
            "name": "详细分析测试",
            "query": "请详细分析财富系列寿险计划的合规要求和风险点",
            "response_type": "detailed",
            "max_tokens": 1024,
            "use_rag": True,
            "timeout": 80
        },
        {
            "name": "深度分析测试",
            "query": "请从法律、技术、管理等多个维度深度分析财富系列寿险计划的合规性，并提供具体的实施建议",
            "response_type": "analysis",
            "max_tokens": 2048,
            "use_rag": True,
            "timeout": 120
        },
        {
            "name": "简单问题快速测试",
            "query": "你好",
            "response_type": "quick",
            "max_tokens": 128,
            "use_rag": False,
            "timeout": 15
        }
    ]
    
    # 执行测试
    print(f"\n🧪 开始执行 {len(test_cases)} 个测试用例...")
    results = test_performance_optimization(token, test_cases)
    
    # 分析结果
    analyze_results(results)
    
    # 保存结果到文件
    with open("performance_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 测试结果已保存到: performance_test_results.json")
    print("\n🎉 性能优化测试完成！")

if __name__ == "__main__":
    main()
