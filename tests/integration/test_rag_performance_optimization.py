#!/usr/bin/env python3
"""
RAG检索性能优化测试脚本
"""

import asyncio
import time
import json
import requests
from typing import List, Dict, Any
import statistics

# 配置
BASE_URL = "http://localhost:8888"
TEST_QUERIES = [
    {
        "query": "什么是数据合规？",
        "type": "simple",
        "expected_docs": 1
    },
    {
        "query": "GDPR的主要要求是什么？",
        "type": "standard", 
        "expected_docs": 3
    },
    {
        "query": "请详细分析数据合规管理系统的实施步骤和最佳实践",
        "type": "complex",
        "expected_docs": 5
    }
]

class RAGPerformanceTester:
    """RAG性能测试器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []
        self.token = None
    
    def login(self) -> bool:
        """登录获取token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "username": "test@example.com",
                    "password": "testpassword123"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("access_token")
                print(f"✅ 登录成功")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 登录错误: {e}")
            return False
    
    async def test_rag_query(
        self, 
        query: str, 
        response_type: str = "standard",
        use_rag: bool = True,
        max_tokens: int = 256
    ) -> Dict[str, Any]:
        """测试RAG查询性能"""
        # 测试聊天API不需要认证
        headers = {}
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/test/chat",
                headers=headers,
                json={
                    "message": query,
                    "use_rag": use_rag,
                    "response_type": response_type,
                    "max_tokens": max_tokens
                },
                timeout=60
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response_time": response_time,
                    "response_length": len(result.get("response", "")),
                    "used_rag": result.get("used_rag", False),
                    "performance": result.get("performance", {}),
                    "response": result.get("response", "")[:200] + "..." if len(result.get("response", "")) > 200 else result.get("response", "")
                }
            else:
                return {
                    "success": False,
                    "response_time": response_time,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "response_time": time.time() - start_time,
                "error": "timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e)
            }
    
    async def run_performance_test(self) -> Dict[str, Any]:
        """运行性能测试"""
        print("🚀 开始RAG性能优化测试")
        
        # 跳过登录，直接测试聊天API
        print("✅ 跳过登录，直接测试聊天API")
        
        test_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": [],
            "summary": {}
        }
        
        # 测试不同配置
        configs = [
            {"response_type": "quick", "max_tokens": 128, "description": "快速模式"},
            {"response_type": "standard", "max_tokens": 256, "description": "标准模式"},
            {"response_type": "detailed", "max_tokens": 512, "description": "详细模式"}
        ]
        
        for config in configs:
            print(f"\n📋 测试配置: {config['description']}")
            config_results = []
            
            for test_query in TEST_QUERIES:
                print(f"  🔍 测试查询: {test_query['query'][:30]}...")
                
                # 测试RAG模式
                rag_result = await self.test_rag_query(
                    test_query["query"],
                    response_type=config["response_type"],
                    use_rag=True,
                    max_tokens=config["max_tokens"]
                )
                
                # 测试非RAG模式
                non_rag_result = await self.test_rag_query(
                    test_query["query"],
                    response_type=config["response_type"],
                    use_rag=False,
                    max_tokens=config["max_tokens"]
                )
                
                test_result = {
                    "query": test_query["query"],
                    "query_type": test_query["type"],
                    "config": config,
                    "rag_result": rag_result,
                    "non_rag_result": non_rag_result,
                    "performance_comparison": {
                        "rag_time": rag_result.get("response_time", 0),
                        "non_rag_time": non_rag_result.get("response_time", 0),
                        "time_difference": (rag_result.get("response_time", 0) - non_rag_result.get("response_time", 0)),
                        "rag_success": rag_result.get("success", False),
                        "non_rag_success": non_rag_result.get("success", False)
                    }
                }
                
                config_results.append(test_result)
                
                # 打印结果
                if rag_result.get("success"):
                    print(f"    ✅ RAG: {rag_result['response_time']:.2f}秒, 长度: {rag_result['response_length']}字符")
                else:
                    print(f"    ❌ RAG: 失败 - {rag_result.get('error', '未知错误')}")
                
                if non_rag_result.get("success"):
                    print(f"    ✅ 非RAG: {non_rag_result['response_time']:.2f}秒, 长度: {non_rag_result['response_length']}字符")
                else:
                    print(f"    ❌ 非RAG: 失败 - {non_rag_result.get('error', '未知错误')}")
            
            test_results["tests"].append({
                "config": config,
                "results": config_results
            })
        
        # 计算汇总统计
        test_results["summary"] = self._calculate_summary(test_results["tests"])
        
        return test_results
    
    def _calculate_summary(self, tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算汇总统计"""
        summary = {
            "total_tests": 0,
            "successful_tests": 0,
            "rag_times": [],
            "non_rag_times": [],
            "performance_improvements": []
        }
        
        for test_group in tests:
            for test_result in test_group["results"]:
                summary["total_tests"] += 1
                
                rag_result = test_result["rag_result"]
                non_rag_result = test_result["non_rag_result"]
                
                if rag_result.get("success"):
                    summary["successful_tests"] += 1
                    summary["rag_times"].append(rag_result["response_time"])
                
                if non_rag_result.get("success"):
                    summary["non_rag_times"].append(non_rag_result["response_time"])
                
                # 计算性能改进
                if rag_result.get("success") and non_rag_result.get("success"):
                    improvement = ((non_rag_result["response_time"] - rag_result["response_time"]) / non_rag_result["response_time"]) * 100
                    summary["performance_improvements"].append(improvement)
        
        # 计算统计指标
        if summary["rag_times"]:
            summary["avg_rag_time"] = statistics.mean(summary["rag_times"])
            summary["min_rag_time"] = min(summary["rag_times"])
            summary["max_rag_time"] = max(summary["rag_times"])
        
        if summary["non_rag_times"]:
            summary["avg_non_rag_time"] = statistics.mean(summary["non_rag_times"])
            summary["min_non_rag_time"] = min(summary["non_rag_times"])
            summary["max_non_rag_time"] = max(summary["non_rag_times"])
        
        if summary["performance_improvements"]:
            summary["avg_improvement"] = statistics.mean(summary["performance_improvements"])
            summary["max_improvement"] = max(summary["performance_improvements"])
            summary["min_improvement"] = min(summary["performance_improvements"])
        
        summary["success_rate"] = (summary["successful_tests"] / summary["total_tests"]) * 100 if summary["total_tests"] > 0 else 0
        
        return summary
    
    def print_summary(self, results: Dict[str, Any]):
        """打印测试汇总"""
        summary = results.get("summary", {})
        
        print("\n" + "="*60)
        print("📊 RAG性能优化测试汇总")
        print("="*60)
        
        print(f"总测试数: {summary.get('total_tests', 0)}")
        print(f"成功测试数: {summary.get('successful_tests', 0)}")
        print(f"成功率: {summary.get('success_rate', 0):.1f}%")
        
        if summary.get("avg_rag_time"):
            print(f"\nRAG响应时间:")
            print(f"  平均: {summary['avg_rag_time']:.2f}秒")
            print(f"  最小: {summary['min_rag_time']:.2f}秒")
            print(f"  最大: {summary['max_rag_time']:.2f}秒")
        
        if summary.get("avg_non_rag_time"):
            print(f"\n非RAG响应时间:")
            print(f"  平均: {summary['avg_non_rag_time']:.2f}秒")
            print(f"  最小: {summary['min_non_rag_time']:.2f}秒")
            print(f"  最大: {summary['max_non_rag_time']:.2f}秒")
        
        if summary.get("avg_improvement") is not None:
            print(f"\n性能改进:")
            print(f"  平均改进: {summary['avg_improvement']:.1f}%")
            print(f"  最大改进: {summary['max_improvement']:.1f}%")
            print(f"  最小改进: {summary['min_improvement']:.1f}%")
        
        print("="*60)
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """保存测试结果"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"rag_performance_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 测试结果已保存到: {filename}")


async def main():
    """主函数"""
    tester = RAGPerformanceTester()
    
    try:
        # 运行性能测试
        results = await tester.run_performance_test()
        
        if "error" in results:
            print(f"❌ 测试失败: {results['error']}")
            return
        
        # 打印汇总
        tester.print_summary(results)
        
        # 保存结果
        tester.save_results(results)
        
        print("\n🎉 RAG性能优化测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
