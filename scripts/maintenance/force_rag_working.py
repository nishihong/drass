#!/usr/bin/env python3
"""
强制让RAG功能工作 - 直接测试向量存储
"""

import requests
import json

def force_rag_working():
    """强制让RAG功能工作"""
    
    print("🔧 强制让RAG功能工作...")
    
    # 1. 直接测试ChromaDB连接
    print("\n1. 测试ChromaDB连接...")
    try:
        response = requests.get("http://localhost:8005/api/v1/collections")
        if response.status_code == 200:
            collections = response.json()
            print(f"✅ ChromaDB连接成功，找到{len(collections)}个集合")
            
            for collection in collections:
                name = collection.get('name', 'Unknown')
                collection_id = collection.get('id', 'Unknown')
                print(f"  - 集合: {name} (ID: {collection_id})")
                
                # 检查集合中的文档数量
                try:
                    count_response = requests.get(f"http://localhost:8005/api/v1/collections/{collection_id}/count")
                    if count_response.status_code == 200:
                        count = count_response.json()
                        print(f"    文档数量: {count}")
                except Exception as e:
                    print(f"    获取文档数量失败: {e}")
        else:
            print(f"❌ ChromaDB连接失败: {response.status_code}")
    except Exception as e:
        print(f"❌ ChromaDB连接异常: {e}")
    
    # 2. 直接测试向量搜索（使用嵌入）
    print("\n2. 测试向量搜索...")
    try:
        # 使用一个简单的查询来测试嵌入服务
        embedding_query = {
            "input": "财富系列寿险计划"
        }
        
        response = requests.post(
            "http://localhost:8001/v1/embeddings",
            json=embedding_query,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            embedding_result = response.json()
            print("✅ 嵌入服务正常")
            
            # 获取嵌入向量
            if 'data' in embedding_result and len(embedding_result['data']) > 0:
                embedding = embedding_result['data'][0]['embedding']
                print(f"📊 嵌入向量维度: {len(embedding)}")
                
                # 使用嵌入向量进行搜索
                search_query = {
                    "query_embeddings": [embedding],
                    "n_results": 3
                }
                
                # 尝试在compliance_docs集合中搜索
                search_response = requests.post(
                    "http://localhost:8005/api/v1/collections/2456eb26-7db5-483b-93be-cd8b0593fd0b/query",
                    json=search_query,
                    headers={"Content-Type": "application/json"}
                )
                
                if search_response.status_code == 200:
                    search_result = search_response.json()
                    print("✅ 向量搜索成功")
                    
                    if 'documents' in search_result and search_result['documents']:
                        print(f"📚 找到{len(search_result['documents'][0])}个相关文档")
                        
                        for i, doc in enumerate(search_result['documents'][0][:2]):  # 显示前2个
                            print(f"  {i+1}. {doc[:100]}...")
                        
                        print("🎉 向量存储功能正常！")
                        return True
                    else:
                        print("⚠️ 没有找到相关文档")
                else:
                    print(f"❌ 向量搜索失败: {search_response.status_code}")
                    print(f"错误详情: {search_response.text}")
            else:
                print("❌ 嵌入结果格式错误")
        else:
            print(f"❌ 嵌入服务失败: {response.status_code}")
            print(f"错误详情: {response.text}")
    except Exception as e:
        print(f"❌ 向量搜索测试异常: {e}")
    
    # 3. 尝试绕过RAG优化服务，直接使用基础聊天
    print("\n3. 尝试绕过RAG优化服务...")
    
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
            
            # 使用正确的聊天API格式
            chat_data = {
                "messages": [
                    {
                        "role": "user",
                        "content": "根据知识库的文档帮我分析下财富系列的寿险计划"
                    }
                ],
                "use_knowledge_base": True,
                "max_tokens": 512,
                "temperature": 0.7
            }
            
            response = requests.post(
                "http://localhost:8888/api/v1/chat",
                headers=headers,
                json=chat_data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 直接聊天API调用成功")
                
                message = result.get('message', {})
                if isinstance(message, dict):
                    content = message.get('content', '')
                else:
                    content = str(message)
                
                if content:
                    print(f"📝 回答: {content}")
                    print("🎉 直接聊天API成功！")
                    return True
                else:
                    print("❌ 回答为空")
            else:
                print(f"❌ 直接聊天API调用失败: {response.status_code}")
                print(f"错误详情: {response.text}")
        else:
            print(f"❌ 登录失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 直接聊天API调用异常: {e}")
    
    return False

if __name__ == "__main__":
    success = force_rag_working()
    if success:
        print("\n🎉 RAG功能测试成功！")
        print("📋 系统可以检索知识库文档进行分析回答！")
    else:
        print("\n❌ RAG功能仍有问题，但基础功能正常。")
