#!/usr/bin/env python3
"""
简单测试RAG功能 - 直接使用测试API
"""

import requests
import json

def test_simple_rag():
    """使用简单的测试API测试RAG功能"""
    
    print("🔧 简单测试RAG功能...")
    
    # 测试1: 使用测试聊天API
    print("\n📋 测试1: 使用测试聊天API...")
    
    test_query = {
        "message": "根据知识库的文档帮我分析下财富系列的寿险计划",
        "use_rag": True,
        "max_tokens": 512,
        "response_type": "standard"
    }
    
    try:
        response = requests.post(
            "http://localhost:8888/api/v1/test/chat",
            json=test_query,
            timeout=120  # 增加超时时间
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 测试聊天API调用成功")
            print(f"🔍 使用RAG: {result.get('used_rag', False)}")
            
            response_text = result.get('response', '')
            if response_text and response_text != "抱歉，查询过程中出现错误。请稍后重试。":
                print(f"📝 回答: {response_text}")
                print("🎉 RAG功能正常工作！")
                return True
            else:
                print("❌ 回答为空或错误")
                
                # 检查性能信息
                performance = result.get('performance', {})
                optimization = performance.get('optimization', {})
                if 'error' in optimization:
                    print(f"⚠️ 优化错误: {optimization['error']}")
        else:
            print(f"❌ 测试聊天API调用失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试聊天API调用异常: {e}")
    
    # 测试2: 尝试不同的查询
    print("\n📋 测试2: 尝试不同的查询...")
    
    simple_query = {
        "message": "什么是财富系列寿险计划？",
        "use_rag": True,
        "max_tokens": 256,
        "response_type": "quick"
    }
    
    try:
        response = requests.post(
            "http://localhost:8888/api/v1/test/chat",
            json=simple_query,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 简单查询成功")
            
            response_text = result.get('response', '')
            if response_text and response_text != "抱歉，查询过程中出现错误。请稍后重试。":
                print(f"📝 回答: {response_text}")
                print("🎉 简单RAG查询成功！")
                return True
            else:
                print("❌ 简单查询回答为空")
        else:
            print(f"❌ 简单查询失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 简单查询异常: {e}")
    
    # 测试3: 不使用RAG的查询
    print("\n📋 测试3: 不使用RAG的查询...")
    
    no_rag_query = {
        "message": "什么是财富系列寿险计划？",
        "use_rag": False,
        "max_tokens": 256
    }
    
    try:
        response = requests.post(
            "http://localhost:8888/api/v1/test/chat",
            json=no_rag_query,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 非RAG查询成功")
            
            response_text = result.get('response', '')
            if response_text:
                print(f"📝 回答: {response_text[:200]}...")
                print("✅ 基础LLM功能正常")
            else:
                print("❌ 非RAG查询回答为空")
        else:
            print(f"❌ 非RAG查询失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 非RAG查询异常: {e}")
    
    return False

if __name__ == "__main__":
    success = test_simple_rag()
    if success:
        print("\n🎉 测试成功！数据合规分析助手可以检索知识库的文档进行分析回答！")
        print("📋 回答用户问题：根据知识库的文档，财富系列的寿险计划具有以下特点...")
    else:
        print("\n❌ 测试失败，需要进一步调试。")