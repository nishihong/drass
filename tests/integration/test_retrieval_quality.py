#!/usr/bin/env python3
"""
检索质量测试脚本
验证RAG检索结果的相关性、测试不同查询类型的准确性、评估用户满意度
"""

import asyncio
import time
import json
import requests
import aiohttp
from typing import List, Dict, Any
import statistics
import re

# 配置
BASE_URL = "http://localhost:8888"
TEST_QUERIES = {
    "basic_knowledge": [
        {
            "query": "什么是数据合规？",
            "expected_keywords": ["数据合规", "数据保护", "法规", "合规管理"],
            "expected_concepts": ["数据保护", "合规要求", "法规遵循"]
        },
        {
            "query": "GDPR的主要要求是什么？",
            "expected_keywords": ["GDPR", "个人数据", "同意", "数据主体权利"],
            "expected_concepts": ["数据保护", "隐私权", "数据主体权利"]
        },
        {
            "query": "数据保护的基本原则有哪些？",
            "expected_keywords": ["合法性", "公平性", "透明性", "目的限制"],
            "expected_concepts": ["数据保护原则", "合法性基础", "目的限制"]
        }
    ],
    "practical_application": [
        {
            "query": "如何实施数据合规管理？",
            "expected_keywords": ["实施", "合规管理", "流程", "技术措施"],
            "expected_concepts": ["合规实施", "管理流程", "技术措施"]
        },
        {
            "query": "数据泄露的应对措施是什么？",
            "expected_keywords": ["数据泄露", "应对", "通知", "补救措施"],
            "expected_concepts": ["事件响应", "通知义务", "补救措施"]
        },
        {
            "query": "数据跨境传输的合规要求有哪些？",
            "expected_keywords": ["跨境传输", "合规要求", "充分性认定", "标准合同条款"],
            "expected_concepts": ["跨境传输", "充分性认定", "标准合同条款"]
        }
    ],
    "complex_analysis": [
        {
            "query": "请详细分析数据合规管理系统的实施步骤和最佳实践",
            "expected_keywords": ["实施步骤", "最佳实践", "系统架构", "管理流程"],
            "expected_concepts": ["系统实施", "最佳实践", "架构设计"]
        },
        {
            "query": "请全面分析GDPR、个人信息保护法、数据安全法等法规的异同点",
            "expected_keywords": ["GDPR", "个人信息保护法", "数据安全法", "异同点"],
            "expected_concepts": ["法规比较", "异同分析", "合规策略"]
        },
        {
            "query": "请详细说明数据保护影响评估(DPIA)的完整流程",
            "expected_keywords": ["DPIA", "影响评估", "风险评估", "流程"],
            "expected_concepts": ["影响评估", "风险评估", "评估流程"]
        }
    ]
}

class RetrievalQualityTester:
    """检索质量测试器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []
    
    async def test_query_quality(
        self, 
        session: aiohttp.ClientSession,
        test_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """测试单个查询的检索质量"""
        query = test_case["query"]
        expected_keywords = test_case["expected_keywords"]
        expected_concepts = test_case["expected_concepts"]
        
        start_time = time.time()
        
        try:
            # 测试RAG模式
            async with session.post(
                f"{self.base_url}/api/v1/test/chat",
                json={
                    "message": query,
                    "use_rag": True,
                    "response_type": "detailed",
                    "max_tokens": 512
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as rag_response:
                rag_end_time = time.time()
                rag_response_time = rag_end_time - start_time
                
                if rag_response.status == 200:
                    rag_result = await rag_response.json()
                    rag_response_text = rag_result.get("response", "")
                    rag_used_rag = rag_result.get("used_rag", False)
                else:
                    rag_response_text = ""
                    rag_used_rag = False
                    rag_response_time = time.time() - start_time
            
            # 测试非RAG模式作为对比
            async with session.post(
                f"{self.base_url}/api/v1/test/chat",
                json={
                    "message": query,
                    "use_rag": False,
                    "response_type": "detailed",
                    "max_tokens": 512
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as non_rag_response:
                non_rag_end_time = time.time()
                non_rag_response_time = non_rag_end_time - start_time
                
                if non_rag_response.status == 200:
                    non_rag_result = await non_rag_response.json()
                    non_rag_response_text = non_rag_result.get("response", "")
                else:
                    non_rag_response_text = ""
                    non_rag_response_time = time.time() - start_time
            
            # 分析检索质量
            rag_quality = self._analyze_response_quality(rag_response_text, expected_keywords, expected_concepts)
            non_rag_quality = self._analyze_response_quality(non_rag_response_text, expected_keywords, expected_concepts)
            
            return {
                "query": query,
                "expected_keywords": expected_keywords,
                "expected_concepts": expected_concepts,
                "rag_response": {
                    "text": rag_response_text,
                    "response_time": rag_response_time,
                    "used_rag": rag_used_rag,
                    "quality": rag_quality
                },
                "non_rag_response": {
                    "text": non_rag_response_text,
                    "response_time": non_rag_response_time,
                    "quality": non_rag_quality
                },
                "quality_comparison": {
                    "rag_better": rag_quality["overall_score"] > non_rag_quality["overall_score"],
                    "score_difference": rag_quality["overall_score"] - non_rag_quality["overall_score"],
                    "keyword_improvement": rag_quality["keyword_score"] - non_rag_quality["keyword_score"],
                    "concept_improvement": rag_quality["concept_score"] - non_rag_quality["concept_score"]
                }
            }
            
        except Exception as e:
            return {
                "query": query,
                "error": str(e),
                "rag_response": {"quality": {"overall_score": 0}},
                "non_rag_response": {"quality": {"overall_score": 0}},
                "quality_comparison": {"rag_better": False, "score_difference": 0}
            }
    
    def _analyze_response_quality(
        self, 
        response_text: str, 
        expected_keywords: List[str], 
        expected_concepts: List[str]
    ) -> Dict[str, Any]:
        """分析响应质量"""
        if not response_text:
            return {
                "overall_score": 0,
                "keyword_score": 0,
                "concept_score": 0,
                "keyword_matches": [],
                "concept_matches": [],
                "response_length": 0,
                "quality_assessment": "poor"
            }
        
        # 关键词匹配分析
        keyword_matches = []
        keyword_score = 0
        
        for keyword in expected_keywords:
            if keyword.lower() in response_text.lower():
                keyword_matches.append(keyword)
                keyword_score += 1
        
        keyword_score = (keyword_score / len(expected_keywords)) * 100 if expected_keywords else 0
        
        # 概念匹配分析
        concept_matches = []
        concept_score = 0
        
        for concept in expected_concepts:
            # 使用更灵活的概念匹配
            concept_found = False
            for word in concept.split():
                if word.lower() in response_text.lower():
                    concept_found = True
                    break
            if concept_found:
                concept_matches.append(concept)
                concept_score += 1
        
        concept_score = (concept_score / len(expected_concepts)) * 100 if expected_concepts else 0
        
        # 响应长度分析
        response_length = len(response_text)
        length_score = min(100, (response_length / 200) * 100)  # 期望至少200字符
        
        # 计算总体质量分数
        overall_score = (keyword_score * 0.4 + concept_score * 0.4 + length_score * 0.2)
        
        # 质量评估
        if overall_score >= 80:
            quality_assessment = "excellent"
        elif overall_score >= 60:
            quality_assessment = "good"
        elif overall_score >= 40:
            quality_assessment = "moderate"
        else:
            quality_assessment = "poor"
        
        return {
            "overall_score": overall_score,
            "keyword_score": keyword_score,
            "concept_score": concept_score,
            "length_score": length_score,
            "keyword_matches": keyword_matches,
            "concept_matches": concept_matches,
            "response_length": response_length,
            "quality_assessment": quality_assessment
        }
    
    async def test_query_category(self, category: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """测试特定查询类别的检索质量"""
        print(f"\n📋 测试 {category} 类别")
        
        # 创建HTTP会话
        connector = aiohttp.TCPConnector(limit=5, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=60)
        
        results = []
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for i, test_case in enumerate(test_cases):
                print(f"  🔍 测试查询 {i+1}: {test_case['query'][:50]}...")
                
                result = await self.test_query_quality(session, test_case)
                results.append(result)
                
                if "error" not in result:
                    rag_quality = result["rag_response"]["quality"]
                    non_rag_quality = result["non_rag_response"]["quality"]
                    comparison = result["quality_comparison"]
                    
                    print(f"    RAG质量: {rag_quality['overall_score']:.1f}分 ({rag_quality['quality_assessment']})")
                    print(f"    非RAG质量: {non_rag_quality['overall_score']:.1f}分 ({non_rag_quality['quality_assessment']})")
                    print(f"    质量提升: {'✅' if comparison['rag_better'] else '❌'} "
                          f"({comparison['score_difference']:+.1f}分)")
                else:
                    print(f"    ❌ 测试失败: {result['error']}")
                
                # 短暂等待避免过载
                await asyncio.sleep(1)
        
        return {
            "category": category,
            "results": results,
            "summary": self._calculate_category_summary(results)
        }
    
    def _calculate_category_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算类别汇总统计"""
        successful_results = [r for r in results if "error" not in r]
        
        if not successful_results:
            return {
                "total_queries": len(results),
                "successful_queries": 0,
                "failed_queries": len(results),
                "success_rate": 0,
                "avg_rag_quality": 0,
                "avg_non_rag_quality": 0,
                "quality_improvement": 0,
                "rag_better_count": 0,
                "quality_improvement_rate": 0
            }
        
        rag_scores = [r["rag_response"]["quality"]["overall_score"] for r in successful_results]
        non_rag_scores = [r["non_rag_response"]["quality"]["overall_score"] for r in successful_results]
        rag_better_count = sum(1 for r in successful_results if r["quality_comparison"]["rag_better"])
        
        return {
            "total_queries": len(results),
            "successful_queries": len(successful_results),
            "failed_queries": len(results) - len(successful_results),
            "success_rate": (len(successful_results) / len(results)) * 100,
            "avg_rag_quality": statistics.mean(rag_scores),
            "avg_non_rag_quality": statistics.mean(non_rag_scores),
            "quality_improvement": statistics.mean(rag_scores) - statistics.mean(non_rag_scores),
            "rag_better_count": rag_better_count,
            "quality_improvement_rate": (rag_better_count / len(successful_results)) * 100
        }
    
    async def run_retrieval_quality_test(self) -> Dict[str, Any]:
        """运行检索质量测试"""
        print("🚀 开始检索质量测试")
        
        test_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "category_tests": [],
            "overall_summary": {}
        }
        
        # 测试所有查询类别
        for category, test_cases in TEST_QUERIES.items():
            result = await self.test_query_category(category, test_cases)
            test_results["category_tests"].append(result)
        
        # 计算整体汇总
        test_results["overall_summary"] = self._calculate_overall_summary(test_results["category_tests"])
        
        return test_results
    
    def _calculate_overall_summary(self, category_tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算整体汇总统计"""
        all_rag_scores = []
        all_non_rag_scores = []
        all_rag_better = []
        
        for test in category_tests:
            summary = test.get("summary", {})
            if summary.get("successful_queries", 0) > 0:
                # 从结果中提取分数
                for result in test["results"]:
                    if "error" not in result:
                        all_rag_scores.append(result["rag_response"]["quality"]["overall_score"])
                        all_non_rag_scores.append(result["non_rag_response"]["quality"]["overall_score"])
                        all_rag_better.append(result["quality_comparison"]["rag_better"])
        
        total_queries = sum(test.get("summary", {}).get("total_queries", 0) for test in category_tests)
        total_successful = len(all_rag_scores)
        
        return {
            "total_queries": total_queries,
            "total_successful": total_successful,
            "overall_success_rate": (total_successful / total_queries) * 100 if total_queries > 0 else 0,
            "avg_rag_quality": statistics.mean(all_rag_scores) if all_rag_scores else 0,
            "avg_non_rag_quality": statistics.mean(all_non_rag_scores) if all_non_rag_scores else 0,
            "overall_quality_improvement": statistics.mean(all_rag_scores) - statistics.mean(all_non_rag_scores) if all_rag_scores and all_non_rag_scores else 0,
            "rag_better_count": sum(all_rag_better),
            "overall_quality_improvement_rate": (sum(all_rag_better) / len(all_rag_better)) * 100 if all_rag_better else 0,
            "quality_assessment": self._assess_overall_quality(statistics.mean(all_rag_scores) if all_rag_scores else 0)
        }
    
    def _assess_overall_quality(self, avg_quality: float) -> str:
        """评估整体质量"""
        if avg_quality >= 80:
            return "excellent"
        elif avg_quality >= 60:
            return "good"
        elif avg_quality >= 40:
            return "moderate"
        else:
            return "poor"
    
    def print_summary(self, results: Dict[str, Any]):
        """打印测试汇总"""
        overall_summary = results.get("overall_summary", {})
        category_tests = results.get("category_tests", [])
        
        print("\n" + "="*60)
        print("📊 检索质量测试汇总")
        print("="*60)
        
        print(f"总查询数: {overall_summary.get('total_queries', 0)}")
        print(f"成功查询数: {overall_summary.get('total_successful', 0)}")
        print(f"整体成功率: {overall_summary.get('overall_success_rate', 0):.1f}%")
        print(f"RAG平均质量: {overall_summary.get('avg_rag_quality', 0):.1f}分")
        print(f"非RAG平均质量: {overall_summary.get('avg_non_rag_quality', 0):.1f}分")
        print(f"质量提升: {overall_summary.get('overall_quality_improvement', 0):+.1f}分")
        print(f"RAG更优查询数: {overall_summary.get('rag_better_count', 0)}")
        print(f"质量提升率: {overall_summary.get('overall_quality_improvement_rate', 0):.1f}%")
        print(f"整体质量评估: {overall_summary.get('quality_assessment', 'unknown')}")
        
        print(f"\n各类别详细结果:")
        for test in category_tests:
            summary = test.get("summary", {})
            category = test.get("category", "unknown")
            
            print(f"  {category.upper()}类别:")
            print(f"    成功率: {summary.get('success_rate', 0):.1f}%")
            print(f"    RAG平均质量: {summary.get('avg_rag_quality', 0):.1f}分")
            print(f"    非RAG平均质量: {summary.get('avg_non_rag_quality', 0):.1f}分")
            print(f"    质量提升: {summary.get('quality_improvement', 0):+.1f}分")
            print(f"    质量提升率: {summary.get('quality_improvement_rate', 0):.1f}%")
        
        print("="*60)
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """保存测试结果"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"retrieval_quality_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 测试结果已保存到: {filename}")


async def main():
    """主函数"""
    tester = RetrievalQualityTester()
    
    try:
        # 运行检索质量测试
        results = await tester.run_retrieval_quality_test()
        
        # 打印汇总
        tester.print_summary(results)
        
        # 保存结果
        tester.save_results(results)
        
        print("\n🎉 检索质量测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
