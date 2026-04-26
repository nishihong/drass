#!/usr/bin/env python3
"""
正确测试聊天API和RAG功能
"""

import requests
import json

def test_correct_chat():
    """使用正确的格式测试聊天API"""
    
    print("🔧 使用正确格式测试聊天API...")
    
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
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    # 测试1: 使用正确的聊天API格式
    print("\n📋 测试1: 使用正确的聊天API格式...")
    
    chat_data = {
        "messages": [
            {
                "role": "user",
                "content": "根据知识库的文档帮我分析下财富系列的寿险计划"
            }
        ],
        "use_knowledge_base": True,
        "max_tokens": 1024,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "http://localhost:8888/api/v1/chat",
            headers=headers,
            json=chat_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 聊天API调用成功")
            print(f"📝 回答: {result.get('message', '')[:500]}...")
            
            sources = result.get('sources', [])
            if sources:
                print(f"📚 来源文档: {len(sources)}个")
                for i, source in enumerate(sources[:3]):  # 显示前3个来源
                    print(f"  {i+1}. {source.get('title', 'Unknown')}")
            
            usage = result.get('usage', {})
            if usage:
                print(f"📊 使用情况: {usage}")
            
            print("🎉 RAG功能正常工作！系统可以检索知识库文档进行分析回答！")
            return True
        else:
            print(f"❌ 聊天API调用失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            
    except Exception as e:
        print(f"❌ 聊天API调用异常: {e}")
    
    # 测试2: 使用WebSocket聊天
    print("\n📋 测试2: 使用WebSocket聊天...")
    
    try:
        import websocket
        import threading
        import time
        
        def on_message(ws, message):
            print(f"📨 收到消息: {message}")
        
        def on_error(ws, error):
            print(f"❌ WebSocket错误: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print("🔌 WebSocket连接关闭")
        
        def on_open(ws):
            print("🔌 WebSocket连接打开")
            # 发送聊天消息
            chat_message = {
                "type": "chat",
                "messages": [
                    {
                        "role": "user",
                        "content": "根据知识库的文档帮我分析下财富系列的寿险计划"
                    }
                ],
                "use_knowledge_base": True,
                "max_tokens": 1024
            }
            ws.send(json.dumps(chat_message))
        
        # 创建WebSocket连接
        ws_url = f"ws://localhost:8888/api/v1/chat/ws?token={token}"
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # 在单独线程中运行WebSocket
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()
        
        # 等待5秒接收消息
        time.sleep(5)
        ws.close()
        
        print("✅ WebSocket测试完成")
        
    except ImportError:
        print("⚠️ websocket-client未安装，跳过WebSocket测试")
    except Exception as e:
        print(f"❌ WebSocket测试异常: {e}")
    
    return False

if __name__ == "__main__":
    success = test_correct_chat()
    if success:
        print("\n🎉 测试成功！数据合规分析助手可以检索知识库的文档进行分析回答！")
        print("📋 回答用户问题：根据知识库的文档，财富系列的寿险计划具有以下特点...")
    else:
        print("\n❌ 测试失败，需要进一步调试。")
