#!/usr/bin/env python3
"""
测试文档上传和RAG检索功能
"""

import requests
import json
import time

def test_document_upload_and_rag():
    """测试文档上传和RAG检索"""
    
    base_url = "http://localhost:8888"
    
    print("🚀 开始测试文档上传和RAG检索功能...")
    
    # 1. 登录获取token
    print("\n1. 登录获取认证token...")
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
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 上传文档
    print("\n2. 上传测试文档...")
    with open("test_wealth_insurance.md", "rb") as f:
        files = {"file": ("test_wealth_insurance.md", f, "text/markdown")}
        data = {"auto_process": True}
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/documents/upload",
                headers=headers,
                files=files,
                data=data
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 文档上传成功: {result}")
                document_id = result.get("document_id")
            else:
                print(f"❌ 文档上传失败: {response.status_code} - {response.text}")
                return
        except Exception as e:
            print(f"❌ 文档上传异常: {e}")
            return
    
    # 3. 等待文档处理
    print("\n3. 等待文档处理完成...")
    max_wait = 60  # 最多等待60秒
    wait_time = 0
    
    while wait_time < max_wait:
        try:
            response = requests.get(
                f"{base_url}/api/v1/documents/{document_id}",
                headers=headers
            )
            if response.status_code == 200:
                doc_info = response.json()
                status = doc_info.get("status")
                print(f"📋 文档状态: {status}")
                
                if status == "completed":
                    print("✅ 文档处理完成")
                    break
                elif status == "failed":
                    print("❌ 文档处理失败")
                    return
            else:
                print(f"❌ 获取文档状态失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 获取文档状态异常: {e}")
        
        time.sleep(5)
        wait_time += 5
    
    if wait_time >= max_wait:
        print("⏰ 文档处理超时")
        return
    
    # 4. 测试RAG检索
    print("\n4. 测试RAG检索功能...")
    chat_data = {
        "message": "根据知识库的文档帮我分析下财富系列的寿险计划",
        "use_rag": True,
        "max_tokens": 1024
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/test/chat",
            json=chat_data
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ RAG检索测试成功")
            print(f"📝 回答: {result.get('response', '')[:200]}...")
            print(f"🔍 使用RAG: {result.get('used_rag', False)}")
            print(f"⏱️ 响应时间: {result.get('performance', {}).get('response_time', 0)}秒")
        else:
            print(f"❌ RAG检索测试失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ RAG检索测试异常: {e}")
    
    # 5. 检查文档列表
    print("\n5. 检查文档列表...")
    try:
        response = requests.get(
            f"{base_url}/api/v1/documents/",
            headers=headers
        )
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ 文档列表获取成功，共{len(docs)}个文档")
            for doc in docs:
                print(f"  - {doc.get('filename', 'Unknown')}: {doc.get('status', 'Unknown')}")
        else:
            print(f"❌ 获取文档列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取文档列表异常: {e}")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_document_upload_and_rag()
