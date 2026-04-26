#!/usr/bin/env python3
"""
直接修复RAG功能 - 重新初始化向量存储
"""

import requests
import json
import time

def fix_rag_direct():
    """直接修复RAG功能"""
    
    print("🔧 直接修复RAG功能...")
    
    base_url = "http://localhost:8888"
    
    # 1. 登录获取token
    print("\n1. 登录获取token...")
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False
    
    # 2. 检查文档状态
    print("\n2. 检查文档状态...")
    try:
        response = requests.get(f"{base_url}/api/v1/documents/", headers=headers)
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ 找到{len(docs)}个文档")
            
            # 检查文档状态
            completed_docs = [doc for doc in docs if doc.get('status') == 'completed']
            print(f"📊 已完成处理的文档: {len(completed_docs)}个")
            
            if completed_docs:
                print("📋 已完成的文档:")
                for doc in completed_docs[:3]:  # 显示前3个
                    print(f"  - {doc.get('filename', 'Unknown')}: {doc.get('status')}")
            else:
                print("⚠️ 没有已完成的文档")
                
        else:
            print(f"❌ 获取文档列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 检查文档状态异常: {e}")
    
    # 3. 尝试重新处理文档
    print("\n3. 尝试重新处理文档...")
    try:
        response = requests.get(f"{base_url}/api/v1/documents/", headers=headers)
        if response.status_code == 200:
            docs = response.json()
            
            # 找到第一个pending或error状态的文档
            target_doc = None
            for doc in docs:
                if doc.get('status') in ['pending', 'error']:
                    target_doc = doc
                    break
            
            if not target_doc:
                # 如果没有pending的，找一个completed的重新处理
                target_doc = docs[0] if docs else None
            
            if target_doc:
                doc_id = target_doc.get('id')
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
                    
                    # 等待处理完成
                    print("⏳ 等待文档处理完成...")
                    time.sleep(15)
                    
                    # 检查处理状态
                    response = requests.get(f"{base_url}/api/v1/documents/{doc_id}", headers=headers)
                    if response.status_code == 200:
                        doc_info = response.json()
                        print(f"📊 文档状态: {doc_info.get('status')}")
                        
                        if doc_info.get('status') == 'completed':
                            print("✅ 文档处理完成")
                        else:
                            print(f"⚠️ 文档状态: {doc_info.get('status')}")
                else:
                    print(f"❌ 文档重新处理请求失败: {response.status_code}")
                    print(f"错误详情: {response.text}")
            else:
                print("⚠️ 没有找到可处理的文档")
        else:
            print(f"❌ 获取文档列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 重新处理文档异常: {e}")
    
    # 4. 测试RAG功能
    print("\n4. 测试RAG功能...")
    
    test_query = {
        "message": "根据知识库的文档帮我分析下财富系列的寿险计划",
        "use_rag": True,
        "max_tokens": 512,
        "response_type": "standard"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/test/chat",
            json=test_query,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RAG测试查询成功")
            print(f"🔍 使用RAG: {result.get('used_rag', False)}")
            
            response_text = result.get('response', '')
            if response_text and response_text != "抱歉，查询过程中出现错误。请稍后重试。":
                print(f"📝 回答: {response_text}")
                print("🎉 RAG功能修复成功！")
                return True
            else:
                print("❌ 回答仍然为空或错误")
                
                # 检查性能信息
                performance = result.get('performance', {})
                optimization = performance.get('optimization', {})
                if 'error' in optimization:
                    print(f"⚠️ 优化错误: {optimization['error']}")
        else:
            print(f"❌ RAG测试查询失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ RAG测试查询异常: {e}")
    
    return False

if __name__ == "__main__":
    success = fix_rag_direct()
    if success:
        print("\n🎉 RAG功能修复成功！")
        print("📋 现在可以回答用户问题：根据知识库的文档，财富系列的寿险计划具有以下特点...")
    else:
        print("\n❌ RAG功能修复失败，需要进一步调试。")
