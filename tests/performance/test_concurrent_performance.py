#!/usr/bin/env python3
"""
并发性能测试脚本
测试RAG优化系统的多用户并发查询能力和系统稳定性
"""

import asyncio
import time
import json
import requests
import aiohttp
from typing import List, Dict, Any
import statistics
import psutil
import os

# 配置
BASE_URL = "http://localhost:8888"
CONCURRENT_USERS = [5, 10, 20, 50]  # 测试不同并发用户数
TEST_QUERIES = [
    "什么是数据合规？",
    "GDPR的主要要求是什么？",
    "数据保护的基本原则有哪些？",
    "如何实施数据合规管理？",
    "数据泄露的应对措施是什么？",
    "个人信息保护法的主要内容？",
    "数据跨境传输的合规要求？",
    "数据安全技术措施有哪些？",
    "数据合规审计的要点？",
    "数据保护影响评估如何进行？"
]

class ConcurrentPerformanceTester:
    """并发性能测试器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []
        self.system_stats = []
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统资源使用情况"""
        try:
            process = psutil.Process(os.getpid())
            return {
                "timestamp": time.time(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_used_mb": psutil.virtual_memory().used / 1024 / 1024,
                "memory_available_mb": psutil.virtual_memory().available / 1024 / 1024,
                "process_memory_mb": process.memory_info().rss / 1024 / 1024,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
        except Exception as e:
            return {
                "timestamp": time.time(),
                "error": str(e)
            }
    
    async def single_query(self, session: aiohttp.ClientSession, query: str, user_id: int) -> Dict[str, Any]:
        """单个查询请求"""
        start_time = time.time()
        
        try:
            async with session.post(
                f"{self.base_url}/api/v1/test/chat",
                json={
                    "message": query,
                    "use_rag": True,
                    "response_type": "standard",
                    "max_tokens": 256
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        "user_id": user_id,
                        "query": query,
                        "success": True,
                        "response_time": response_time,
                        "response_length": len(result.get("response", "")),
                        "used_rag": result.get("used_rag", False),
                        "status_code": response.status
                    }
                else:
                    return {
                        "user_id": user_id,
                        "query": query,
                        "success": False,
                        "response_time": response_time,
                        "error": f"HTTP {response.status}",
                        "status_code": response.status
                    }
                    
        except asyncio.TimeoutError:
            return {
                "user_id": user_id,
                "query": query,
                "success": False,
                "response_time": time.time() - start_time,
                "error": "timeout"
            }
        except Exception as e:
            return {
                "user_id": user_id,
                "query": query,
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e)
            }
    
    async def concurrent_test(self, num_users: int, queries_per_user: int = 3) -> Dict[str, Any]:
        """并发测试"""
        print(f"🚀 开始 {num_users} 用户并发测试")
        
        # 记录测试开始时的系统状态
        start_stats = self.get_system_stats()
        
        # 创建HTTP会话
        connector = aiohttp.TCPConnector(limit=num_users * 2, limit_per_host=num_users * 2)
        timeout = aiohttp.ClientTimeout(total=60)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 创建并发任务
            tasks = []
            for user_id in range(num_users):
                for i in range(queries_per_user):
                    query = TEST_QUERIES[i % len(TEST_QUERIES)]
                    task = self.single_query(session, query, user_id)
                    tasks.append(task)
            
            # 执行并发请求
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # 记录测试结束时的系统状态
            end_stats = self.get_system_stats()
        
        # 处理结果
        successful_results = []
        failed_results = []
        
        for result in results:
            if isinstance(result, Exception):
                failed_results.append({
                    "error": str(result),
                    "type": "exception"
                })
            elif result.get("success"):
                successful_results.append(result)
            else:
                failed_results.append(result)
        
        # 计算统计信息
        total_requests = len(tasks)
        successful_requests = len(successful_results)
        failed_requests = len(failed_results)
        success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        
        response_times = [r["response_time"] for r in successful_results]
        
        test_result = {
            "num_users": num_users,
            "queries_per_user": queries_per_user,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": success_rate,
            "total_time": end_time - start_time,
            "requests_per_second": total_requests / (end_time - start_time) if (end_time - start_time) > 0 else 0,
            "response_times": {
                "avg": statistics.mean(response_times) if response_times else 0,
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "p95": self._percentile(response_times, 95) if response_times else 0,
                "p99": self._percentile(response_times, 99) if response_times else 0
            },
            "system_stats": {
                "start": start_stats,
                "end": end_stats
            },
            "failed_results": failed_results[:10]  # 只保留前10个失败结果
        }
        
        # 打印结果
        print(f"  📊 测试结果:")
        print(f"    总请求数: {total_requests}")
        print(f"    成功请求: {successful_requests}")
        print(f"    失败请求: {failed_requests}")
        print(f"    成功率: {success_rate:.1f}%")
        print(f"    总耗时: {test_result['total_time']:.2f}秒")
        print(f"    请求/秒: {test_result['requests_per_second']:.2f}")
        print(f"    平均响应时间: {test_result['response_times']['avg']:.3f}秒")
        print(f"    95%响应时间: {test_result['response_times']['p95']:.3f}秒")
        
        return test_result
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        if index >= len(sorted_data):
            index = len(sorted_data) - 1
        return sorted_data[index]
    
    async def run_concurrent_tests(self) -> Dict[str, Any]:
        """运行并发性能测试"""
        print("🚀 开始并发性能测试")
        
        test_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "concurrent_tests": [],
            "summary": {}
        }
        
        # 测试不同并发用户数
        for num_users in CONCURRENT_USERS:
            print(f"\n👥 测试 {num_users} 个并发用户")
            
            # 记录测试前系统状态
            pre_test_stats = self.get_system_stats()
            
            # 执行并发测试
            result = await self.concurrent_test(num_users)
            test_results["concurrent_tests"].append(result)
            
            # 记录测试后系统状态
            post_test_stats = self.get_system_stats()
            
            # 等待系统稳定
            await asyncio.sleep(2)
        
        # 计算汇总统计
        test_results["summary"] = self._calculate_concurrent_summary(test_results["concurrent_tests"])
        
        return test_results
    
    def _calculate_concurrent_summary(self, tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算并发测试汇总统计"""
        summary = {
            "max_concurrent_users": max(t["num_users"] for t in tests),
            "max_requests_per_second": max(t["requests_per_second"] for t in tests),
            "min_success_rate": min(t["success_rate"] for t in tests),
            "avg_success_rate": statistics.mean(t["success_rate"] for t in tests),
            "max_avg_response_time": max(t["response_times"]["avg"] for t in tests),
            "min_avg_response_time": min(t["response_times"]["avg"] for t in tests),
            "max_p95_response_time": max(t["response_times"]["p95"] for t in tests),
            "system_stability": "stable" if all(t["success_rate"] > 90 for t in tests) else "unstable"
        }
        
        return summary
    
    def print_summary(self, results: Dict[str, Any]):
        """打印测试汇总"""
        summary = results.get("summary", {})
        
        print("\n" + "="*60)
        print("📊 并发性能测试汇总")
        print("="*60)
        
        print(f"最大并发用户数: {summary.get('max_concurrent_users', 0)}")
        print(f"最大请求/秒: {summary.get('max_requests_per_second', 0):.2f}")
        print(f"最低成功率: {summary.get('min_success_rate', 0):.1f}%")
        print(f"平均成功率: {summary.get('avg_success_rate', 0):.1f}%")
        print(f"最大平均响应时间: {summary.get('max_avg_response_time', 0):.3f}秒")
        print(f"最小平均响应时间: {summary.get('min_avg_response_time', 0):.3f}秒")
        print(f"最大95%响应时间: {summary.get('max_p95_response_time', 0):.3f}秒")
        print(f"系统稳定性: {summary.get('system_stability', 'unknown')}")
        
        print("="*60)
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """保存测试结果"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"concurrent_performance_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 测试结果已保存到: {filename}")


async def main():
    """主函数"""
    tester = ConcurrentPerformanceTester()
    
    try:
        # 运行并发性能测试
        results = await tester.run_concurrent_tests()
        
        # 打印汇总
        tester.print_summary(results)
        
        # 保存结果
        tester.save_results(results)
        
        print("\n🎉 并发性能测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
