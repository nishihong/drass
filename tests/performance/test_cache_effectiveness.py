#!/usr/bin/env python3
"""
缓存效果测试脚本
测试RAG优化系统的缓存命中率、数据正确性和清理功能
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
    "什么是数据合规？",
    "GDPR的主要要求是什么？",
    "数据保护的基本原则有哪些？",
    "什么是数据合规？",  # 重复查询测试缓存
    "GDPR的主要要求是什么？",  # 重复查询测试缓存
]

class CacheEffectivenessTester:
    """缓存效果测试器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []
    
    async def test_query_with_cache(
        self, 
        query: str, 
        response_type: str = "standard",
        use_rag: bool = True,
        max_tokens: int = 256
    ) -> Dict[str, Any]:
        """测试带缓存的查询"""
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/test/chat",
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
                    "response": result.get("response", "")[:100] + "..." if len(result.get("response", "")) > 100 else result.get("response", "")
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
    
    async def test_cache_clear(self) -> Dict[str, Any]:
        """测试缓存清理功能"""
        try:
            # 测试RAG优化API的缓存清理
            response = requests.post(
                f"{self.base_url}/api/v1/rag-optimization/clear-cache",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message": result.get("message", "缓存清理成功"),
                    "cleared_items": result.get("cleared_items", 0)
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_cache_stats(self) -> Dict[str, Any]:
        """测试缓存统计信息"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/rag-optimization/stats",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "stats": result
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_cache_test(self) -> Dict[str, Any]:
        """运行缓存效果测试"""
        print("🚀 开始缓存效果测试")
        
        test_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "cache_tests": [],
            "summary": {}
        }
        
        # 1. 测试缓存统计
        print("\n📊 测试缓存统计信息")
        cache_stats = await self.test_cache_stats()
        if cache_stats.get("success"):
            print(f"✅ 缓存统计获取成功: {cache_stats['stats']}")
        else:
            print(f"❌ 缓存统计获取失败: {cache_stats.get('error')}")
        
        # 2. 测试重复查询的缓存效果
        print("\n🔄 测试重复查询缓存效果")
        first_run_times = []
        second_run_times = []
        
        for i, query in enumerate(TEST_QUERIES):
            print(f"  🔍 测试查询 {i+1}: {query[:30]}...")
            
            # 第一次查询
            first_result = await self.test_query_with_cache(query)
            if first_result.get("success"):
                first_run_times.append(first_result["response_time"])
                print(f"    ✅ 第一次: {first_result['response_time']:.3f}秒")
            else:
                print(f"    ❌ 第一次: 失败 - {first_result.get('error')}")
            
            # 短暂等待
            await asyncio.sleep(0.1)
            
            # 第二次查询（应该命中缓存）
            second_result = await self.test_query_with_cache(query)
            if second_result.get("success"):
                second_run_times.append(second_result["response_time"])
                print(f"    ✅ 第二次: {second_result['response_time']:.3f}秒")
                
                # 计算缓存效果
                if first_result.get("success"):
                    speedup = first_result["response_time"] / second_result["response_time"] if second_result["response_time"] > 0 else 0
                    print(f"    📈 加速比: {speedup:.2f}x")
            else:
                print(f"    ❌ 第二次: 失败 - {second_result.get('error')}")
            
            test_results["cache_tests"].append({
                "query": query,
                "first_run": first_result,
                "second_run": second_result,
                "speedup": first_result.get("response_time", 0) / second_result.get("response_time", 1) if second_result.get("success") and first_result.get("success") else 0
            })
        
        # 3. 测试缓存清理
        print("\n🧹 测试缓存清理功能")
        clear_result = await self.test_cache_clear()
        if clear_result.get("success"):
            print(f"✅ 缓存清理成功: {clear_result.get('message')}")
            print(f"   清理项目数: {clear_result.get('cleared_items', 0)}")
        else:
            print(f"❌ 缓存清理失败: {clear_result.get('error')}")
        
        # 4. 清理后再次测试
        print("\n🔄 清理后测试缓存重建")
        await asyncio.sleep(1)  # 等待清理完成
        
        post_clear_times = []
        for i, query in enumerate(TEST_QUERIES[:3]):  # 只测试前3个查询
            print(f"  🔍 清理后查询 {i+1}: {query[:30]}...")
            result = await self.test_query_with_cache(query)
            if result.get("success"):
                post_clear_times.append(result["response_time"])
                print(f"    ✅ 清理后: {result['response_time']:.3f}秒")
            else:
                print(f"    ❌ 清理后: 失败 - {result.get('error')}")
        
        # 计算汇总统计
        test_results["summary"] = self._calculate_cache_summary(
            first_run_times, second_run_times, post_clear_times, cache_stats
        )
        
        return test_results
    
    def _calculate_cache_summary(
        self, 
        first_times: List[float], 
        second_times: List[float], 
        post_clear_times: List[float],
        cache_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """计算缓存效果汇总统计"""
        summary = {
            "cache_stats": cache_stats.get("stats", {}),
            "first_run_avg": statistics.mean(first_times) if first_times else 0,
            "second_run_avg": statistics.mean(second_times) if second_times else 0,
            "post_clear_avg": statistics.mean(post_clear_times) if post_clear_times else 0,
            "cache_hit_improvement": 0,
            "cache_effectiveness": "unknown"
        }
        
        if first_times and second_times:
            # 计算缓存命中后的平均加速比
            speedups = []
            for i in range(min(len(first_times), len(second_times))):
                if second_times[i] > 0:
                    speedup = first_times[i] / second_times[i]
                    speedups.append(speedup)
            
            if speedups:
                summary["cache_hit_improvement"] = statistics.mean(speedups)
                
                # 评估缓存效果
                if summary["cache_hit_improvement"] > 2.0:
                    summary["cache_effectiveness"] = "excellent"
                elif summary["cache_hit_improvement"] > 1.5:
                    summary["cache_effectiveness"] = "good"
                elif summary["cache_hit_improvement"] > 1.1:
                    summary["cache_effectiveness"] = "moderate"
                else:
                    summary["cache_effectiveness"] = "poor"
        
        return summary
    
    def print_summary(self, results: Dict[str, Any]):
        """打印测试汇总"""
        summary = results.get("summary", {})
        
        print("\n" + "="*60)
        print("📊 缓存效果测试汇总")
        print("="*60)
        
        print(f"缓存统计: {summary.get('cache_stats', {})}")
        print(f"第一次查询平均时间: {summary.get('first_run_avg', 0):.3f}秒")
        print(f"第二次查询平均时间: {summary.get('second_run_avg', 0):.3f}秒")
        print(f"清理后查询平均时间: {summary.get('post_clear_avg', 0):.3f}秒")
        print(f"缓存命中加速比: {summary.get('cache_hit_improvement', 0):.2f}x")
        print(f"缓存效果评估: {summary.get('cache_effectiveness', 'unknown')}")
        
        print("="*60)
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """保存测试结果"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"cache_effectiveness_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 测试结果已保存到: {filename}")


async def main():
    """主函数"""
    tester = CacheEffectivenessTester()
    
    try:
        # 运行缓存效果测试
        results = await tester.run_cache_test()
        
        # 打印汇总
        tester.print_summary(results)
        
        # 保存结果
        tester.save_results(results)
        
        print("\n🎉 缓存效果测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
