#!/usr/bin/env python3
"""
文档上传和删除功能测试脚本
"""

import requests
import json
import os
import time

# API配置
BASE_URL = "http://localhost:8888/api/v1"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

def login():
    """登录获取访问令牌"""
    print("🔐 正在登录...")
    
    form_data = {
        'username': TEST_USER['email'],
        'password': TEST_USER['password']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=form_data)
        response.raise_for_status()
        
        data = response.json()
        token = data['access_token']
        print(f"✅ 登录成功！Token: {token[:20]}...")
        return token
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 登录失败: {e}")
        return None

def get_documents(token):
    """获取文档列表"""
    print("\n📋 正在获取文档列表...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/documents/", headers=headers)
        response.raise_for_status()
        
        documents = response.json()
        print(f"✅ 获取文档列表成功！找到 {len(documents)} 个文档")
        
        for doc in documents:
            print(f"  - {doc['name']} ({doc['type']}, {doc['size']} bytes, {doc['status']})")
        
        return documents
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取文档列表失败: {e}")
        return []

def upload_document(token, file_path):
    """上传文档"""
    print(f"\n📤 正在上传文档: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return None
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/plain')}
            response = requests.post(f"{BASE_URL}/documents/upload", headers=headers, files=files)
        
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ 文档上传成功！文档ID: {result['id']}")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 文档上传失败: {e}")
        return None

def delete_document(token, document_id):
    """删除文档"""
    print(f"\n🗑️ 正在删除文档: {document_id}")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.delete(f"{BASE_URL}/documents/{document_id}", headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ 文档删除成功！")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 文档删除失败: {e}")
        return False

def create_test_file():
    """创建测试文件"""
    test_content = f"""# 测试文档

这是一个用于测试文档上传功能的测试文件。

创建时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
测试内容: 数据合规管理系统文档上传功能测试

## 测试要点

1. 文档上传功能
2. 文档列表显示
3. 文档删除功能
4. API认证机制

## 测试结果

如果这个文档能够成功上传、显示和删除，说明文档管理功能正常工作。
"""
    
    test_file_path = "/tmp/test_document.md"
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"📝 创建测试文件: {test_file_path}")
    return test_file_path

def main():
    """主测试流程"""
    print("🚀 开始文档上传和删除功能测试")
    print("=" * 50)
    
    # 1. 登录
    token = login()
    if not token:
        print("❌ 无法获取访问令牌，测试终止")
        return
    
    # 2. 获取初始文档列表
    initial_docs = get_documents(token)
    
    # 3. 创建并上传测试文档
    test_file = create_test_file()
    uploaded_doc = upload_document(token, test_file)
    
    if not uploaded_doc:
        print("❌ 文档上传失败，测试终止")
        return
    
    # 4. 验证文档是否出现在列表中
    print("\n🔍 验证文档是否出现在列表中...")
    updated_docs = get_documents(token)
    
    doc_found = any(doc['id'] == uploaded_doc['id'] for doc in updated_docs)
    if doc_found:
        print("✅ 文档成功出现在列表中！")
    else:
        print("❌ 文档未出现在列表中")
    
    # 5. 删除测试文档
    delete_success = delete_document(token, uploaded_doc['id'])
    
    # 6. 验证文档是否已删除
    print("\n🔍 验证文档是否已删除...")
    final_docs = get_documents(token)
    
    doc_still_exists = any(doc['id'] == uploaded_doc['id'] for doc in final_docs)
    if not doc_still_exists:
        print("✅ 文档已成功删除！")
    else:
        print("❌ 文档仍然存在于列表中")
    
    # 7. 清理测试文件
    try:
        os.remove(test_file)
        print(f"🧹 清理测试文件: {test_file}")
    except:
        pass
    
    # 8. 测试总结
    print("\n" + "=" * 50)
    print("📊 测试总结:")
    print(f"  - 登录: {'✅ 成功' if token else '❌ 失败'}")
    print(f"  - 文档上传: {'✅ 成功' if uploaded_doc else '❌ 失败'}")
    print(f"  - 文档列表显示: {'✅ 成功' if doc_found else '❌ 失败'}")
    print(f"  - 文档删除: {'✅ 成功' if delete_success else '❌ 失败'}")
    print(f"  - 删除验证: {'✅ 成功' if not doc_still_exists else '❌ 失败'}")
    
    if token and uploaded_doc and doc_found and delete_success and not doc_still_exists:
        print("\n🎉 所有测试通过！文档上传和删除功能正常工作。")
    else:
        print("\n⚠️ 部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
