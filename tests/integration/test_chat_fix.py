#!/usr/bin/env python3
"""
测试聊天功能修复的脚本
"""

import asyncio
import httpx
import json
import re

async def test_vllm_direct():
    """直接测试VLLM服务"""
    print("🔍 测试VLLM服务...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                'http://localhost:8001/v1/chat/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer 123456'
                },
                json={
                    'model': 'vllm',
                    'messages': [{'role': 'user', 'content': '请解释一下什么是数据合规'}],
                    'max_tokens': 500,
                    'temperature': 0.7
                },
                timeout=30.0
            )
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print("✅ VLLM服务正常")
                print(f"📝 原始回答长度: {len(content)} 字符")
                
                # 移除think标签
                clean_content = re.sub(r'<think>.*?</think>\s*', '', content, flags=re.DOTALL)
                clean_content = clean_content.strip()
                print(f"🧹 清理后回答长度: {len(clean_content)} 字符")
                print(f"📄 回答内容: {clean_content[:200]}...")
                return True
            else:
                print(f"❌ VLLM服务错误: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ VLLM服务连接失败: {e}")
            return False

async def test_backend_api():
    """测试后端API"""
    print("\n🔍 测试后端API...")
    async with httpx.AsyncClient() as client:
        try:
            # 测试健康检查
            response = await client.get('http://localhost:8888/health', timeout=10.0)
            if response.status_code == 200:
                print("✅ 后端API健康检查通过")
                
                # 测试聊天端点
                chat_response = await client.post(
                    'http://localhost:8888/api/v1/test/chat',
                    headers={'Content-Type': 'application/json'},
                    json={
                        'message': '请解释一下什么是数据合规',
                        'use_rag': False
                    },
                    timeout=30.0
                )
                if chat_response.status_code == 200:
                    result = chat_response.json()
                    print("✅ 聊天API正常")
                    print(f"📝 回答: {result.get('response', '')[:200]}...")
                    return True
                else:
                    print(f"❌ 聊天API错误: {chat_response.status_code}")
                    return False
            else:
                print(f"❌ 后端API健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 后端API连接失败: {e}")
            return False

async def main():
    print("🚀 开始测试聊天功能修复...")
    print("=" * 50)
    
    # 测试VLLM服务
    vllm_ok = await test_vllm_direct()
    
    # 测试后端API
    backend_ok = await test_backend_api()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"  VLLM服务: {'✅ 正常' if vllm_ok else '❌ 异常'}")
    print(f"  后端API: {'✅ 正常' if backend_ok else '❌ 异常'}")
    
    if vllm_ok and backend_ok:
        print("\n🎉 恭喜！聊天功能修复成功！")
        print("💡 现在您可以在前端界面中正常使用聊天功能了")
        print("🌐 访问地址: http://localhost:5173")
    elif vllm_ok:
        print("\n⚠️  VLLM服务正常，但后端API需要重启")
        print("💡 建议运行: ./start-compliance-assistant.sh")
    else:
        print("\n❌ 需要检查VLLM服务状态")

if __name__ == "__main__":
    asyncio.run(main())
