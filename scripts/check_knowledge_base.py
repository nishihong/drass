#!/usr/bin/env python3
"""
检查知识库中的文档
"""

import requests
import json

def check_knowledge_base():
    """检查知识库中的文档"""
    
    print("📚 检查知识库中的文档...")
    
    # 1. 登录获取token
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post("http://localhost:8888/api/v1/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    # 2. 获取文档列表
    print("\n📋 获取文档列表...")
    try:
        response = requests.get("http://localhost:8888/api/v1/documents/", headers=headers)
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ 找到{len(docs)}个文档")
            
            for i, doc in enumerate(docs, 1):
                print(f"\n📄 文档 {i}:")
                print(f"  - ID: {doc.get('id', 'Unknown')}")
                print(f"  - 文件名: {doc.get('filename', 'Unknown')}")
                print(f"  - 状态: {doc.get('status', 'Unknown')}")
                print(f"  - 大小: {doc.get('size', 'Unknown')} bytes")
                print(f"  - 上传时间: {doc.get('uploaded_at', 'Unknown')}")
                print(f"  - 处理时间: {doc.get('processed_at', 'Unknown')}")
                
                # 如果有内容预览，显示前200个字符
                if 'content' in doc and doc['content']:
                    content_preview = doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
                    print(f"  - 内容预览: {content_preview}")
                
                # 如果有元数据，显示关键信息
                if 'metadata' in doc and doc['metadata']:
                    metadata = doc['metadata']
                    print(f"  - 元数据: {json.dumps(metadata, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 获取文档列表失败: {response.status_code}")
            print(f"错误详情: {response.text}")
    except Exception as e:
        print(f"❌ 获取文档列表异常: {e}")
    
    # 3. 尝试获取特定文档的详细内容
    print("\n📖 获取文档详细内容...")
    try:
        response = requests.get("http://localhost:8888/api/v1/documents/", headers=headers)
        if response.status_code == 200:
            docs = response.json()
            
            # 找一个已完成的文档
            completed_doc = None
            for doc in docs:
                if doc.get('status') == 'completed':
                    completed_doc = doc
                    break
            
            if completed_doc:
                doc_id = completed_doc.get('id')
                print(f"📄 获取文档详细内容: {doc_id}")
                
                response = requests.get(f"http://localhost:8888/api/v1/documents/{doc_id}", headers=headers)
                if response.status_code == 200:
                    doc_detail = response.json()
                    print("✅ 文档详细信息:")
                    print(f"  - 文件名: {doc_detail.get('filename', 'Unknown')}")
                    print(f"  - 状态: {doc_detail.get('status', 'Unknown')}")
                    print(f"  - 大小: {doc_detail.get('size', 'Unknown')} bytes")
                    
                    # 显示内容
                    if 'content' in doc_detail and doc_detail['content']:
                        content = doc_detail['content']
                        print(f"  - 内容长度: {len(content)} 字符")
                        print(f"  - 内容预览: {content[:500]}...")
                    else:
                        print("  - 内容: 无内容或内容为空")
                    
                    # 显示处理结果
                    if 'processing_result' in doc_detail and doc_detail['processing_result']:
                        result = doc_detail['processing_result']
                        print(f"  - 处理结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                else:
                    print(f"❌ 获取文档详情失败: {response.status_code}")
            else:
                print("⚠️ 没有找到已完成的文档")
        else:
            print(f"❌ 获取文档列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取文档详情异常: {e}")
    
    # 4. 测试文档搜索功能
    print("\n🔍 测试文档搜索功能...")
    try:
        search_data = {
            "query": "财富系列寿险计划",
            "limit": 3
        }
        
        response = requests.post(
            "http://localhost:8888/api/v1/documents/search",
            headers=headers,
            json=search_data
        )
        
        if response.status_code == 200:
            search_results = response.json()
            print("✅ 文档搜索成功")
            print(f"📊 找到{len(search_results)}个相关文档")
            
            for i, result in enumerate(search_results, 1):
                print(f"\n📄 搜索结果 {i}:")
                print(f"  - 文档ID: {result.get('document_id', 'Unknown')}")
                print(f"  - 相似度: {result.get('similarity', 'Unknown')}")
                print(f"  - 内容片段: {result.get('content', 'Unknown')[:200]}...")
        else:
            print(f"❌ 文档搜索失败: {response.status_code}")
            print(f"错误详情: {response.text}")
    except Exception as e:
        print(f"❌ 文档搜索异常: {e}")

if __name__ == "__main__":
    check_knowledge_base()
