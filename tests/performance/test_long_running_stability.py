#!/usr/bin/env python3
"""
长时间运行稳定性测试脚本
测试RAG优化系统在5分钟内的稳定性、内存使用情况和性能衰减
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
import threading
from datetime import datetime, timedelta

# 配置
BASE_URL = "http://localhost:8888"
TEST_DURATION_MINUTES = 1
TEST_INTERVAL_SECONDS = 10
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

class LongRunningStabilityTester:
    """长时间运行稳定性测试器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []
        self.system_stats = []
        self.test_start_time = None
        self.test_end_time = None
        self.monitoring_active = False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统资源使用情况"""
        try:
            process = psutil.Process(os.getpid())
            return {
                "timestamp": time.time(),
                "datetime": datetime.now().isoformat(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_used_mb": psutil.virtual_memory().used / 1024 / 1024,
                "memory_available_mb": psutil.virtual_memory().available / 1024 / 1024,
                "process_memory_mb": process.memory_info().rss / 1024 / 1024,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
            }
        except Exception as e:
            return {
                "timestamp": time.time(),
                "datetime": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def single_query(self, session: aiohttp.ClientSession, query: str) -> Dict[str, Any]:
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
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "response_time": response_time,
                        "response_length": len(result.get("response", "")),
                        "used_rag": result.get("used_rag", False),
                        "status_code": response.status,
                        "timestamp": start_time
                    }
                else:
                    return {
                        "success": False,
                        "response_time": response_time,
                        "error": f"HTTP {response.status}",
                        "status_code": response.status,
                        "timestamp": start_time
                    }
                    
        except asyncio.TimeoutError:
            return {
                "success": False,
                "response_time": time.time() - start_time,
                "error": "timeout",
                "timestamp": start_time
            }
        except Exception as e:
            return {
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e),
                "timestamp": start_time
            }
    
    async def system_monitor(self):
        """系统监控线程"""
        while self.monitoring_active:
            stats = self.get_system_stats()
            self.system_stats.append(stats)
            await asyncio.sleep(5)  # 每5秒记录一次系统状态
    
    async def stability_test_cycle(self, session: aiohttp.ClientSession, cycle_num: int) -> Dict[str, Any]:
        """稳定性测试周期"""
        print(f"  🔄 测试周期 {cycle_num}")
        
        # 执行多个查询
        tasks = []
        for i in range(5):  # 每个周期执行5个查询
            query = TEST_QUERIES[i % len(TEST_QUERIES)]
            task = self.single_query(session, query)
            tasks.append(task)
        
        # 等待所有查询完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
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
        
        # 计算周期统计
        cycle_stats = {
            "cycle_num": cycle_num,
            "timestamp": time.time(),
            "total_queries": len(tasks),
            "successful_queries": len(successful_results),
            "failed_queries": len(failed_results),
            "success_rate": (len(successful_results) / len(tasks)) * 100 if tasks else 0,
            "avg_response_time": statistics.mean([r["response_time"] for r in successful_results]) if successful_results else 0,
            "max_response_time": max([r["response_time"] for r in successful_results]) if successful_results else 0,
            "min_response_time": min([r["response_time"] for r in successful_results]) if successful_results else 0
        }
        
        print(f"    ✅ 成功: {cycle_stats['successful_queries']}/{cycle_stats['total_queries']} "
              f"({cycle_stats['success_rate']:.1f}%) "
              f"平均响应: {cycle_stats['avg_response_time']:.3f}秒")
        
        return cycle_stats
    
    async def run_stability_test(self) -> Dict[str, Any]:
        """运行长时间稳定性测试"""
        print(f"🚀 开始 {TEST_DURATION_MINUTES} 分钟稳定性测试")
        
        self.test_start_time = time.time()
        self.monitoring_active = True
        
        # 启动系统监控
        monitor_task = asyncio.create_task(self.system_monitor())
        
        # 创建HTTP会话
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=30)
        
        test_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_duration_minutes": TEST_DURATION_MINUTES,
            "test_interval_seconds": TEST_INTERVAL_SECONDS,
            "cycles": [],
            "summary": {}
        }
        
        cycle_count = 0
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            while time.time() - self.test_start_time < TEST_DURATION_MINUTES * 60:
                cycle_count += 1
                
                # 执行测试周期
                cycle_result = await self.stability_test_cycle(session, cycle_count)
                test_results["cycles"].append(cycle_result)
                
                # 等待下一个周期
                await asyncio.sleep(TEST_INTERVAL_SECONDS)
        
        self.test_end_time = time.time()
        self.monitoring_active = False
        
        # 停止系统监控
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        
        # 计算汇总统计
        test_results["summary"] = self._calculate_stability_summary(test_results["cycles"])
        test_results["system_stats"] = self.system_stats
        
        return test_results
    
    def _calculate_stability_summary(self, cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算稳定性测试汇总统计"""
        if not cycles:
            return {}
        
        success_rates = [c["success_rate"] for c in cycles]
        response_times = [c["avg_response_time"] for c in cycles if c["avg_response_time"] > 0]
        
        # 计算性能衰减
        first_half = cycles[:len(cycles)//2]
        second_half = cycles[len(cycles)//2:]
        
        first_half_avg = statistics.mean([c["avg_response_time"] for c in first_half if c["avg_response_time"] > 0]) if first_half else 0
        second_half_avg = statistics.mean([c["avg_response_time"] for c in second_half if c["avg_response_time"] > 0]) if second_half else 0
        
        performance_degradation = 0
        if first_half_avg > 0 and second_half_avg > 0:
            performance_degradation = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        summary = {
            "total_cycles": len(cycles),
            "total_queries": sum(c["total_queries"] for c in cycles),
            "total_successful": sum(c["successful_queries"] for c in cycles),
            "total_failed": sum(c["failed_queries"] for c in cycles),
            "overall_success_rate": statistics.mean(success_rates),
            "min_success_rate": min(success_rates),
            "max_success_rate": max(success_rates),
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "performance_degradation_percent": performance_degradation,
            "stability_assessment": self._assess_stability(success_rates, performance_degradation)
        }
        
        return summary
    
    def _assess_stability(self, success_rates: List[float], performance_degradation: float) -> str:
        """评估系统稳定性"""
        avg_success_rate = statistics.mean(success_rates)
        min_success_rate = min(success_rates)
        
        if avg_success_rate >= 95 and min_success_rate >= 90 and abs(performance_degradation) <= 10:
            return "excellent"
        elif avg_success_rate >= 90 and min_success_rate >= 80 and abs(performance_degradation) <= 20:
            return "good"
        elif avg_success_rate >= 80 and min_success_rate >= 70 and abs(performance_degradation) <= 30:
            return "moderate"
        else:
            return "poor"
    
    def print_summary(self, results: Dict[str, Any]):
        """打印测试汇总"""
        summary = results.get("summary", {})
        system_stats = results.get("system_stats", [])
        
        print("\n" + "="*60)
        print("📊 长时间运行稳定性测试汇总")
        print("="*60)
        
        print(f"测试持续时间: {results.get('test_duration_minutes', 0)} 分钟")
        print(f"总测试周期: {summary.get('total_cycles', 0)}")
        print(f"总查询数: {summary.get('total_queries', 0)}")
        print(f"总成功数: {summary.get('total_successful', 0)}")
        print(f"总失败数: {summary.get('total_failed', 0)}")
        print(f"整体成功率: {summary.get('overall_success_rate', 0):.1f}%")
        print(f"最低成功率: {summary.get('min_success_rate', 0):.1f}%")
        print(f"最高成功率: {summary.get('max_success_rate', 0):.1f}%")
        print(f"平均响应时间: {summary.get('avg_response_time', 0):.3f}秒")
        print(f"最小响应时间: {summary.get('min_response_time', 0):.3f}秒")
        print(f"最大响应时间: {summary.get('max_response_time', 0):.3f}秒")
        print(f"性能衰减: {summary.get('performance_degradation_percent', 0):.1f}%")
        print(f"稳定性评估: {summary.get('stability_assessment', 'unknown')}")
        
        # 系统资源使用情况
        if system_stats:
            print(f"\n系统资源使用情况:")
            cpu_usage = [s.get("cpu_percent", 0) for s in system_stats if "cpu_percent" in s]
            memory_usage = [s.get("memory_percent", 0) for s in system_stats if "memory_percent" in s]
            
            if cpu_usage:
                print(f"  CPU使用率: 平均 {statistics.mean(cpu_usage):.1f}%, 最大 {max(cpu_usage):.1f}%")
            if memory_usage:
                print(f"  内存使用率: 平均 {statistics.mean(memory_usage):.1f}%, 最大 {max(memory_usage):.1f}%")
        
        print("="*60)
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """保存测试结果"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"long_running_stability_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 测试结果已保存到: {filename}")


async def main():
    """主函数"""
    tester = LongRunningStabilityTester()
    
    try:
        # 运行长时间稳定性测试
        results = await tester.run_stability_test()
        
        # 打印汇总
        tester.print_summary(results)
        
        # 保存结果
        tester.save_results(results)
        
        print("\n🎉 长时间运行稳定性测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
