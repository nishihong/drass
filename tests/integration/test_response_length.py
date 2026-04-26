#!/usr/bin/env python3
"""
测试数据合规分析助手的回答长度
"""

import requests
import json
import time

# API配置
BASE_URL = "http://localhost:8888/api/v1"

def test_response_length():
    """测试回答长度"""
    print("🧪 测试数据合规分析助手的回答长度")
    print("=" * 50)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(5)
    
    # 测试问题
    test_questions = [
        "分析一下财富系列寿险计划",
        "请详细解释数据合规的重要性",
        "什么是个人信息保护法？请详细说明其主要内容和影响"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 测试问题 {i}: {question}")
        print("-" * 40)
        
        try:
            # 发送请求
            response = requests.post(f"{BASE_URL}/test/chat", json={
                "message": question,
                "use_rag": False,  # 直接使用VLLM
                "temperature": 0.7,
                "max_tokens": 2048  # 使用新的max_tokens设置
            }, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "")
                
                # 计算回答长度
                char_count = len(answer)
                word_count = len(answer.split())
                
                print(f"✅ 回答长度: {char_count} 字符, {word_count} 词")
                print(f"📄 回答内容预览 (前200字符):")
                print(f"   {answer[:200]}...")
                
                # 判断回答是否足够详细
                if char_count > 500:
                    print("✅ 回答长度充足")
                elif char_count > 200:
                    print("⚠️ 回答长度中等")
                else:
                    print("❌ 回答长度较短")
                    
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络错误: {e}")
        except Exception as e:
            print(f"❌ 其他错误: {e}")
        
        print()
    
    print("=" * 50)
    print("🎯 测试完成！")
    print("\n💡 建议:")
    print("   - 如果回答仍然较短，可以进一步增加max_tokens")
    print("   - 可以调整temperature参数来改变回答的创造性")
    print("   - 考虑使用RAG模式来获得更专业的回答")

if __name__ == "__main__":
    test_response_length()
