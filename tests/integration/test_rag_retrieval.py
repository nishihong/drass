#!/usr/bin/env python3
"""
测试数据合规助手的知识库检索功能
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8888"

def login():
    """登录获取token"""
    # 使用form-data格式，OAuth2PasswordRequestForm需要username和password字段
    login_data = {
        "username": "test@example.com",  # OAuth2规范使用username字段
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ 登录成功")
        return token
    else:
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return None

def get_documents(token):
    """获取文档列表"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/documents/", headers=headers)
    
    if response.status_code == 200:
        documents = response.json()
        print(f"📚 知识库中有 {len(documents)} 个文档:")
        for i, doc in enumerate(documents, 1):
            print(f"  {i}. {doc.get('title', 'Unknown')} - {doc.get('status', 'Unknown')}")
        return documents
    else:
        print(f"❌ 获取文档列表失败: {response.status_code} - {response.text}")
        return []

def upload_test_document(token):
    """上传测试文档"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建测试文档内容
    test_content = """
# 财富系列寿险计划合规分析报告

## 产品概述
财富系列寿险计划是一款综合性的寿险产品，旨在为客户提供全面的风险保障和财富增值服务。

## 合规要求分析

### 1. 个人信息保护合规
- 客户信息收集必须遵循《个人信息保护法》相关规定
- 需要获得客户明确同意才能收集敏感信息
- 建立完善的数据安全保护机制

### 2. 金融产品合规
- 产品设计需符合《保险法》和银保监会相关规定
- 销售过程中不得进行虚假宣传
- 需要向客户充分披露产品风险和收益情况

### 3. 数据安全合规
- 建立数据分类分级保护制度
- 实施数据访问控制和审计机制
- 定期进行数据安全评估和风险识别

### 4. 客户权益保护
- 建立客户投诉处理机制
- 提供透明的产品信息和服务条款
- 确保客户知情权和选择权

## 风险识别与建议

### 高风险点
1. 客户信息泄露风险
2. 产品宣传合规风险
3. 数据跨境传输风险

### 合规建议
1. 加强员工合规培训
2. 建立定期合规检查机制
3. 完善内控制度和流程
4. 建立应急响应预案
"""
    
    # 创建测试文档
    files = {
        'file': ('财富系列寿险计划合规分析.md', test_content, 'text/markdown')
    }
    
    data = {
        'title': '财富系列寿险计划合规分析',
        'description': '财富系列寿险计划的合规分析报告，包含个人信息保护、金融产品合规、数据安全合规等方面的详细分析',
        'auto_process': 'true'
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/documents/upload", 
                           headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 测试文档上传成功: {result.get('title', 'Unknown')}")
        return result.get('id')
    else:
        print(f"❌ 文档上传失败: {response.status_code} - {response.text}")
        return None

def test_rag_query(token, query):
    """测试RAG检索查询"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试聊天API
    chat_data = {
        "message": query,
        "use_rag": True,
        "max_tokens": 1024
    }
    
    print(f"\n🔍 测试查询: {query}")
    print("⏳ 正在处理...")
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/test/chat", 
                           headers=headers, json=chat_data, timeout=60)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 查询成功 (耗时: {end_time - start_time:.2f}秒)")
        print(f"📝 回答内容:")
        print("-" * 50)
        print(result.get('message', ''))
        print("-" * 50)
        print(f"🔍 使用RAG: {result.get('used_rag', False)}")
        if result.get('sources'):
            print(f"📚 检索到 {len(result['sources'])} 个相关文档")
        return result
    else:
        print(f"❌ 查询失败: {response.status_code} - {response.text}")
        return None

def main():
    """主函数"""
    print("🚀 开始测试数据合规助手的知识库检索功能")
    print("=" * 60)
    
    # 1. 登录
    token = login()
    if not token:
        return
    
    # 2. 检查现有文档
    print("\n📚 检查知识库中的文档...")
    documents = get_documents(token)
    
    # 3. 如果没有文档，上传测试文档
    if not documents:
        print("\n📤 知识库为空，上传测试文档...")
        doc_id = upload_test_document(token)
        if doc_id:
            print("⏳ 等待文档处理完成...")
            time.sleep(5)  # 等待文档处理
        else:
            print("❌ 无法上传测试文档，测试终止")
            return
    else:
        print("✅ 知识库中已有文档，直接进行测试")
    
    # 4. 测试RAG检索查询
    test_queries = [
        "帮我分析下财富系列寿险计划，并给出报告",
        "财富系列寿险计划有哪些合规要求？",
        "这个产品存在哪些风险点？",
        "如何确保财富系列寿险计划的合规性？"
    ]
    
    print("\n🧪 开始RAG检索测试...")
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- 测试 {i}/{len(test_queries)} ---")
        result = test_rag_query(token, query)
        if result:
            print("✅ 测试通过")
        else:
            print("❌ 测试失败")
        
        if i < len(test_queries):
            time.sleep(2)  # 避免请求过于频繁
    
    print("\n🎉 RAG检索功能测试完成！")

if __name__ == "__main__":
    main()
