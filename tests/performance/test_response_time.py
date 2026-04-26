#!/usr/bin/env python3
"""
响应时间测试脚本
测试RAG优化系统的响应时间是否达到目标：快速查询<2秒、标准查询<5秒、详细查询<15秒
"""

import asyncio
import time
import json
import requests
import aiohttp
from typing import List, Dict, Any
import statistics

# 配置
BASE_URL = "http://localhost:8888"
TEST_QUERIES = {
    "quick": [
        "什么是数据合规？",
        "GDPR是什么？",
        "数据保护的基本原则？",
        "个人信息保护法的主要内容？",
        "数据安全技术措施有哪些？"
    ],
    "standard": [
        "GDPR的主要要求是什么？请详细说明。",
        "如何实施数据合规管理？包括哪些步骤？",
        "数据泄露的应对措施是什么？如何预防？",
        "数据跨境传输的合规要求有哪些？",
        "数据合规审计的要点是什么？如何进行？"
    ],
    "detailed": [
        "请详细分析数据合规管理系统的实施步骤和最佳实践，包括技术架构、组织架构、流程设计等。",
        "请全面分析GDPR、个人信息保护法、数据安全法等法规的异同点，以及企业如何制定统一的合规策略。",
        "请详细说明数据保护影响评估(DPIA)的完整流程，包括评估标准、方法、工具和实施建议。",
        "请深入分析数据合规管理中的技术措施，包括数据分类、加密、访问控制、监控审计等具体实施方案。",
        "请全面阐述数据合规管理系统的建设方案，包括需求分析、系统设计、实施计划、运维管理等各个方面。"
    ]
}

class ResponseTimeTester:
    """响应时间测试器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []
    
    async def test_query_response_time(
        self, 
        session: aiohttp.ClientSession,
        query: str, 
        response_type: str,
        max_tokens: int
    ) -> Dict[str, Any]:
        """测试单个查询的响应时间"""
        start_time = time.time()
        
        try:
            async with session.post(
                f"{self.base_url}/api/v1/test/chat",
                json={
                    "message": query,
                    "use_rag": True,
                    "response_type": response_type,
                    "max_tokens": max_tokens
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        "query": query,
                        "response_type": response_type,
                        "max_tokens": max_tokens,
                        "success": True,
                        "response_time": response_time,
                        "response_length": len(result.get("response", "")),
                        "used_rag": result.get("used_rag", False),
                        "status_code": response.status,
                        "meets_target": self._check_response_time_target(response_type, response_time)
                    }
                else:
                    return {
                        "query": query,
                        "response_type": response_type,
                        "max_tokens": max_tokens,
                        "success": False,
                        "response_time": response_time,
                        "error": f"HTTP {response.status}",
                        "status_code": response.status,
                        "meets_target": False
                    }
                    
        except asyncio.TimeoutError:
            return {
                "query": query,
                "response_type": response_type,
                "max_tokens": max_tokens,
                "success": False,
                "response_time": time.time() - start_time,
                "error": "timeout",
                "meets_target": False
            }
        except Exception as e:
            return {
                "query": query,
                "response_type": response_type,
                "max_tokens": max_tokens,
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e),
                "meets_target": False
            }
    
    def _check_response_time_target(self, response_type: str, response_time: float) -> bool:
        """检查响应时间是否达到目标"""
        targets = {
            "quick": 2.0,    # 快速查询 < 2秒
            "standard": 5.0,  # 标准查询 < 5秒
            "detailed": 15.0  # 详细查询 < 15秒
        }
        return response_time <= targets.get(response_type, 15.0)
    
    async def test_response_type(self, response_type: str, queries: List[str]) -> Dict[str, Any]:
        """测试特定响应类型的所有查询"""
        print(f"\n📋 测试 {response_type} 模式")
        
        # 配置参数
        configs = {
            "quick": {"max_tokens": 128, "description": "快速模式"},
            "standard": {"max_tokens": 256, "description": "标准模式"},
            "detailed": {"max_tokens": 512, "description": "详细模式"}
        }
        
        config = configs.get(response_type, {"max_tokens": 256, "description": "默认模式"})
        
        # 创建HTTP会话
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=60)
        
        results = []
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for i, query in enumerate(queries):
                print(f"  🔍 测试查询 {i+1}: {query[:50]}...")
                
                result = await self.test_query_response_time(
                    session, query, response_type, config["max_tokens"]
                )
                results.append(result)
                
                if result.get("success"):
                    status = "✅" if result.get("meets_target") else "⚠️"
                    print(f"    {status} 响应时间: {result['response_time']:.3f}秒 "
                          f"(目标: <{configs[response_type]['max_tokens']/128*2:.1f}秒)")
                else:
                    print(f"    ❌ 失败: {result.get('error', '未知错误')}")
                
                # 短暂等待避免过载
                await asyncio.sleep(0.5)
        
        return {
            "response_type": response_type,
            "config": config,
            "results": results,
            "summary": self._calculate_response_type_summary(results, response_type)
        }
    
    def _calculate_response_type_summary(self, results: List[Dict[str, Any]], response_type: str) -> Dict[str, Any]:
        """计算响应类型汇总统计"""
        successful_results = [r for r in results if r.get("success")]
        failed_results = [r for r in results if not r.get("success")]
        
        if not successful_results:
            return {
                "total_queries": len(results),
                "successful_queries": 0,
                "failed_queries": len(failed_results),
                "success_rate": 0,
                "avg_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0,
                "meets_target_count": 0,
                "meets_target_rate": 0,
                "target_achieved": False
            }
        
        response_times = [r["response_time"] for r in successful_results]
        meets_target_count = sum(1 for r in successful_results if r.get("meets_target"))
        
        return {
            "total_queries": len(results),
            "successful_queries": len(successful_results),
            "failed_queries": len(failed_results),
            "success_rate": (len(successful_results) / len(results)) * 100,
            "avg_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "meets_target_count": meets_target_count,
            "meets_target_rate": (meets_target_count / len(successful_results)) * 100,
            "target_achieved": meets_target_count == len(successful_results)
        }
    
    async def run_response_time_test(self) -> Dict[str, Any]:
        """运行响应时间测试"""
        print("🚀 开始响应时间测试")
        
        test_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "response_type_tests": [],
            "overall_summary": {}
        }
        
        # 测试所有响应类型
        for response_type, queries in TEST_QUERIES.items():
            result = await self.test_response_type(response_type, queries)
            test_results["response_type_tests"].append(result)
        
        # 计算整体汇总
        test_results["overall_summary"] = self._calculate_overall_summary(test_results["response_type_tests"])
        
        return test_results
    
    def _calculate_overall_summary(self, response_type_tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算整体汇总统计"""
        all_successful = []
        all_meets_target = []
        
        for test in response_type_tests:
            summary = test.get("summary", {})
            if summary.get("successful_queries", 0) > 0:
                all_successful.extend([r for r in test["results"] if r.get("success")])
                all_meets_target.extend([r for r in test["results"] if r.get("success") and r.get("meets_target")])
        
        total_queries = sum(test.get("summary", {}).get("total_queries", 0) for test in response_type_tests)
        total_successful = len(all_successful)
        total_meets_target = len(all_meets_target)
        
        response_times = [r["response_time"] for r in all_successful]
        
        return {
            "total_queries": total_queries,
            "total_successful": total_successful,
            "total_meets_target": total_meets_target,
            "overall_success_rate": (total_successful / total_queries) * 100 if total_queries > 0 else 0,
            "overall_target_achievement_rate": (total_meets_target / total_successful) * 100 if total_successful > 0 else 0,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "all_targets_achieved": all(test.get("summary", {}).get("target_achieved", False) for test in response_type_tests)
        }
    
    def print_summary(self, results: Dict[str, Any]):
        """打印测试汇总"""
        overall_summary = results.get("overall_summary", {})
        response_type_tests = results.get("response_type_tests", [])
        
        print("\n" + "="*60)
        print("📊 响应时间测试汇总")
        print("="*60)
        
        print(f"总查询数: {overall_summary.get('total_queries', 0)}")
        print(f"成功查询数: {overall_summary.get('total_successful', 0)}")
        print(f"达到目标数: {overall_summary.get('total_meets_target', 0)}")
        print(f"整体成功率: {overall_summary.get('overall_success_rate', 0):.1f}%")
        print(f"目标达成率: {overall_summary.get('overall_target_achievement_rate', 0):.1f}%")
        print(f"平均响应时间: {overall_summary.get('avg_response_time', 0):.3f}秒")
        print(f"最小响应时间: {overall_summary.get('min_response_time', 0):.3f}秒")
        print(f"最大响应时间: {overall_summary.get('max_response_time', 0):.3f}秒")
        print(f"所有目标达成: {'✅' if overall_summary.get('all_targets_achieved', False) else '❌'}")
        
        print(f"\n各响应类型详细结果:")
        for test in response_type_tests:
            summary = test.get("summary", {})
            response_type = test.get("response_type", "unknown")
            target_time = {"quick": 2.0, "standard": 5.0, "detailed": 15.0}.get(response_type, 15.0)
            
            print(f"  {response_type.upper()}模式:")
            print(f"    成功率: {summary.get('success_rate', 0):.1f}%")
            print(f"    平均响应时间: {summary.get('avg_response_time', 0):.3f}秒 (目标: <{target_time}秒)")
            print(f"    目标达成率: {summary.get('meets_target_rate', 0):.1f}%")
            print(f"    目标达成: {'✅' if summary.get('target_achieved', False) else '❌'}")
        
        print("="*60)
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """保存测试结果"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"response_time_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 测试结果已保存到: {filename}")


async def main():
    """主函数"""
    tester = ResponseTimeTester()
    
    try:
        # 运行响应时间测试
        results = await tester.run_response_time_test()
        
        # 打印汇总
        tester.print_summary(results)
        
        # 保存结果
        tester.save_results(results)
        
        print("\n🎉 响应时间测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
