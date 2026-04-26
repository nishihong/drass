#!/usr/bin/env python3
"""
修复向量存储初始化问题
"""

import requests
import json
import time

def fix_vector_store():
    """修复向量存储初始化问题"""
    
    print("🔧 开始修复向量存储初始化问题...")
    
    base_url = "http://localhost:8888"
    
    # 1. 检查当前状态
    print("\n1. 检查当前系统状态...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print("✅ 系统健康检查通过")
            print(f"📊 系统状态: {health}")
        else:
            print(f"❌ 系统健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 系统健康检查异常: {e}")
    
    # 2. 检查RAG优化服务状态
    print("\n2. 检查RAG优化服务状态...")
    try:
        response = requests.get(f"{base_url}/api/v1/rag-optimization/health")
        if response.status_code == 200:
            rag_health = response.json()
            print("✅ RAG优化服务健康检查通过")
            print(f"📊 RAG状态: {rag_health}")
        else:
            print(f"❌ RAG优化服务健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ RAG优化服务健康检查异常: {e}")
    
    # 3. 尝试重新初始化向量存储
    print("\n3. 尝试重新初始化向量存储...")
    
    # 登录获取token
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 4. 检查文档列表
    print("\n4. 检查文档列表...")
    try:
        response = requests.get(f"{base_url}/api/v1/documents/", headers=headers)
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ 文档列表获取成功，共{len(docs)}个文档")
            for doc in docs:
                print(f"  - {doc.get('filename', 'Unknown')}: {doc.get('status', 'Unknown')}")
        else:
            print(f"❌ 获取文档列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取文档列表异常: {e}")
    
    # 5. 尝试触发文档重新处理
    print("\n5. 尝试触发文档重新处理...")
    try:
        # 获取第一个文档ID
        response = requests.get(f"{base_url}/api/v1/documents/", headers=headers)
        if response.status_code == 200:
            docs = response.json()
            if docs:
                doc_id = docs[0].get('id')
                print(f"📋 重新处理文档: {doc_id}")
                
                # 触发重新处理
                process_data = {
                    "auto_process": True,
                    "processing_request": {
                        "chunk_size": 1000,
                        "chunk_overlap": 200,
                        "enable_vectorization": True
                    }
                }
                
                response = requests.post(
                    f"{base_url}/api/v1/documents/{doc_id}/process",
                    headers=headers,
                    json=process_data
                )
                
                if response.status_code == 200:
                    print("✅ 文档重新处理请求成功")
                else:
                    print(f"❌ 文档重新处理请求失败: {response.status_code} - {response.text}")
            else:
                print("⚠️ 没有找到文档")
        else:
            print(f"❌ 获取文档列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 文档重新处理异常: {e}")
    
    # 6. 等待处理完成并测试RAG
    print("\n6. 等待处理完成并测试RAG...")
    time.sleep(10)  # 等待10秒
    
    # 测试RAG功能
    test_query = {
        "message": "根据知识库的文档帮我分析下财富系列的寿险计划",
        "use_rag": True,
        "max_tokens": 512
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/test/chat",
            json=test_query,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RAG测试查询成功")
            print(f"🔍 使用RAG: {result.get('used_rag', False)}")
            
            response_text = result.get('response', '')
            if response_text and response_text != "抱歉，查询过程中出现错误。请稍后重试。":
                print(f"📝 回答: {response_text[:200]}...")
                print("🎉 向量存储修复成功！RAG功能正常工作！")
            else:
                print("❌ 回答仍然为空，需要进一步检查")
                
                # 检查性能信息
                performance = result.get('performance', {})
                optimization = performance.get('optimization', {})
                if 'error' in optimization:
                    print(f"⚠️ 优化错误: {optimization['error']}")
        else:
            print(f"❌ RAG测试查询失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ RAG测试查询异常: {e}")
    
    print("\n🎉 向量存储修复完成！")

if __name__ == "__main__":
    fix_vector_store()
