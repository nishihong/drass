#!/usr/bin/env python3
"""
快速修复RAG功能 - 直接测试现有向量存储
"""

import requests
import json

def test_existing_vector_store():
    """测试现有向量存储功能"""
    
    print("🔧 快速修复RAG功能...")
    
    # 直接测试现有的聊天API，不使用RAG优化
    test_query = {
        "message": "根据知识库的文档帮我分析下财富系列的寿险计划",
        "use_rag": False,  # 先测试不使用RAG
        "max_tokens": 1024
    }
    
    print("📋 测试1: 不使用RAG的查询...")
    try:
        response = requests.post(
            "http://localhost:8888/api/v1/test/chat",
            json=test_query,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 查询成功")
            print(f"🔍 使用RAG: {result.get('used_rag', False)}")
            
            response_text = result.get('response', '')
            if response_text:
                print(f"📝 回答: {response_text[:300]}...")
                print("✅ 基础聊天功能正常")
            else:
                print("❌ 回答为空")
        else:
            print(f"❌ 查询失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 查询异常: {e}")
    
    # 现在测试使用RAG，但使用原始的RAG链
    print("\n📋 测试2: 使用原始RAG链的查询...")
    test_query_rag = {
        "message": "根据知识库的文档帮我分析下财富系列的寿险计划",
        "use_rag": True,
        "max_tokens": 1024
    }
    
    try:
        response = requests.post(
            "http://localhost:8888/api/v1/test/chat",
            json=test_query_rag,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 查询成功")
            print(f"🔍 使用RAG: {result.get('used_rag', False)}")
            
            response_text = result.get('response', '')
            if response_text and response_text != "抱歉，查询过程中出现错误。请稍后重试。":
                print(f"📝 回答: {response_text[:300]}...")
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
            print(f"❌ 查询失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 查询异常: {e}")
    
    # 测试3: 尝试使用原始的合规RAG链
    print("\n📋 测试3: 尝试直接调用合规RAG链...")
    
    # 登录获取token
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post("http://localhost:8888/api/v1/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # 尝试直接调用聊天API
            chat_data = {
                "message": "根据知识库的文档帮我分析下财富系列的寿险计划",
                "session_id": "test_session",
                "use_rag": True
            }
            
            response = requests.post(
                "http://localhost:8888/api/v1/chat",
                headers=headers,
                json=chat_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 直接聊天API调用成功")
                print(f"📝 回答: {result.get('response', '')[:300]}...")
                print("🎉 原始RAG功能正常工作！")
                return True
            else:
                print(f"❌ 直接聊天API调用失败: {response.status_code} - {response.text}")
                
        else:
            print(f"❌ 登录失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 直接聊天API调用异常: {e}")
    
    return False

if __name__ == "__main__":
    success = test_existing_vector_store()
    if success:
        print("\n🎉 RAG功能修复成功！系统可以正常检索知识库文档进行分析回答。")
    else:
        print("\n❌ RAG功能仍有问题，需要进一步调试。")
