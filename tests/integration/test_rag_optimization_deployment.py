#!/usr/bin/env python3
"""
RAG优化服务部署测试脚本
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

class RAGOptimizationTester:
    """RAG优化服务测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8888"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_check(self) -> Dict[str, Any]:
        """测试健康检查"""
        print("🔍 测试RAG优化服务健康检查...")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/rag-optimization/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 健康检查通过: {data}")
                    return {"status": "success", "data": data}
                else:
                    print(f"❌ 健康检查失败: {response.status}")
                    return {"status": "error", "status_code": response.status}
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_performance_stats(self) -> Dict[str, Any]:
        """测试性能统计"""
        print("📊 测试性能统计...")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/rag-optimization/performance-stats") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 性能统计获取成功: {data}")
                    return {"status": "success", "data": data}
                else:
                    print(f"❌ 性能统计获取失败: {response.status}")
                    return {"status": "error", "status_code": response.status}
        except Exception as e:
            print(f"❌ 性能统计异常: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_config(self) -> Dict[str, Any]:
        """测试配置获取"""
        print("⚙️ 测试配置获取...")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/rag-optimization/config") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 配置获取成功: {data}")
                    return {"status": "success", "data": data}
                else:
                    print(f"❌ 配置获取失败: {response.status}")
                    return {"status": "error", "status_code": response.status}
        except Exception as e:
            print(f"❌ 配置获取异常: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_vector_store_stats(self) -> Dict[str, Any]:
        """测试向量存储统计"""
        print("🗄️ 测试向量存储统计...")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/rag-optimization/vector-store-stats") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 向量存储统计获取成功: {data}")
                    return {"status": "success", "data": data}
                else:
                    print(f"❌ 向量存储统计获取失败: {response.status}")
                    return {"status": "error", "status_code": response.status}
        except Exception as e:
            print(f"❌ 向量存储统计异常: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_optimized_query(self, query: str = "什么是数据合规？", response_type: str = "standard") -> Dict[str, Any]:
        """测试优化查询"""
        print(f"🔍 测试优化查询: {query} (类型: {response_type})")
        
        try:
            payload = {
                "query": query,
                "response_type": response_type,
                "use_adaptive": True
            }
            
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/api/v1/rag-optimization/query",
                json=payload
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 优化查询成功: {response_time:.3f}秒")
                    print(f"   回答长度: {len(data.get('answer', ''))}")
                    print(f"   检索文档数: {len(data.get('context', []))}")
                    print(f"   优化策略: {data.get('optimization', {}).get('strategy', 'unknown')}")
                    return {"status": "success", "data": data, "response_time": response_time}
                else:
                    print(f"❌ 优化查询失败: {response.status}")
                    error_text = await response.text()
                    print(f"   错误信息: {error_text}")
                    return {"status": "error", "status_code": response.status, "error": error_text}
        except Exception as e:
            print(f"❌ 优化查询异常: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_different_response_types(self) -> Dict[str, Any]:
        """测试不同响应类型"""
        print("🎯 测试不同响应类型...")
        
        query = "数据合规管理的基本原则是什么？"
        response_types = ["quick", "standard", "detailed"]
        results = {}
        
        for response_type in response_types:
            print(f"\n测试 {response_type} 类型:")
            result = await self.test_optimized_query(query, response_type)
            results[response_type] = result
        
        return {"status": "success", "results": results}
    
    async def test_config_update(self) -> Dict[str, Any]:
        """测试配置更新"""
        print("⚙️ 测试配置更新...")
        
        try:
            payload = {
                "max_retrieval_docs": 2,
                "similarity_threshold": 0.8,
                "enable_cache": True
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/rag-optimization/update-config",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 配置更新成功: {data}")
                    return {"status": "success", "data": data}
                else:
                    print(f"❌ 配置更新失败: {response.status}")
                    return {"status": "error", "status_code": response.status}
        except Exception as e:
            print(f"❌ 配置更新异常: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_clear_cache(self) -> Dict[str, Any]:
        """测试清空缓存"""
        print("🗑️ 测试清空缓存...")
        
        try:
            async with self.session.post(f"{self.base_url}/api/v1/rag-optimization/clear-cache") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 缓存清空成功: {data}")
                    return {"status": "success", "data": data}
                else:
                    print(f"❌ 缓存清空失败: {response.status}")
                    return {"status": "error", "status_code": response.status}
        except Exception as e:
            print(f"❌ 缓存清空异常: {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("🚀 开始RAG优化服务部署测试...")
        print("=" * 60)
        
        test_results = {}
        
        # 基础功能测试
        test_results["health_check"] = await self.test_health_check()
        test_results["performance_stats"] = await self.test_performance_stats()
        test_results["config"] = await self.test_config()
        test_results["vector_store_stats"] = await self.test_vector_store_stats()
        
        # 查询功能测试
        test_results["optimized_query"] = await self.test_optimized_query()
        test_results["different_response_types"] = await self.test_different_response_types()
        
        # 配置管理测试
        test_results["config_update"] = await self.test_config_update()
        test_results["clear_cache"] = await self.test_clear_cache()
        
        # 统计结果
        total_tests = len(test_results)
        successful_tests = sum(1 for result in test_results.values() if result.get("status") == "success")
        
        print("\n" + "=" * 60)
        print("📊 测试结果统计:")
        print(f"总测试数: {total_tests}")
        print(f"成功测试: {successful_tests}")
        print(f"失败测试: {total_tests - successful_tests}")
        print(f"成功率: {successful_tests/total_tests*100:.1f}%")
        
        return {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": successful_tests/total_tests*100
            },
            "results": test_results
        }


async def main():
    """主函数"""
    async with RAGOptimizationTester() as tester:
        results = await tester.run_all_tests()
        
        # 保存测试结果
        with open("rag_optimization_deployment_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 测试结果已保存到: rag_optimization_deployment_test_results.json")
        
        # 返回测试结果
        return results


if __name__ == "__main__":
    asyncio.run(main())
