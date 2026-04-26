#!/usr/bin/env python3
"""
直接测试RAG功能
"""

import requests
import json

def test_rag_direct():
    """直接测试RAG功能"""
    
    print("🚀 直接测试RAG功能...")
    
    # 测试不同的查询方式
    test_queries = [
        {
            "message": "财富系列寿险计划的特点是什么？",
            "use_rag": True,
            "max_tokens": 512
        },
        {
            "message": "根据知识库分析财富系列寿险计划",
            "use_rag": True,
            "max_tokens": 1024
        },
        {
            "message": "什么是财富系列寿险计划？",
            "use_rag": True,
            "max_tokens": 256
        }
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 测试查询 {i}: {query['message']}")
        
        try:
            response = requests.post(
                "http://localhost:8888/api/v1/test/chat",
                json=query,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 查询成功")
                print(f"🔍 使用RAG: {result.get('used_rag', False)}")
                print(f"⏱️ 响应时间: {result.get('performance', {}).get('response_time', 0)}秒")
                
                response_text = result.get('response', '')
                if response_text and response_text != "抱歉，查询过程中出现错误。请稍后重试。":
                    print(f"📝 回答: {response_text[:200]}...")
                    if len(response_text) > 200:
                        print("   (回答被截断)")
                else:
                    print("❌ 回答为空或错误")
                    
                # 检查性能信息
                performance = result.get('performance', {})
                optimization = performance.get('optimization', {})
                if 'error' in optimization:
                    print(f"⚠️ 优化错误: {optimization['error']}")
                    
            else:
                print(f"❌ 查询失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 查询异常: {e}")
    
    print("\n🎉 RAG功能测试完成！")

if __name__ == "__main__":
    test_rag_direct()
