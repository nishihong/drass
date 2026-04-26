#!/usr/bin/env python3
"""
测试RAG修复功能
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append('/home/qwkj/drass/services/main-app')

async def test_rag_chain():
    """测试修复后的RAG链"""
    try:
        from app.chains.compliance_rag_chain import ComplianceRAGChain
        from app.services.vector_store import vector_store_service
        
        print("1. 初始化向量存储服务...")
        await vector_store_service.initialize()
        print(f"   向量存储状态: {vector_store_service.vector_store is not None}")
        
        print("2. 创建RAG链...")
        rag_chain = ComplianceRAGChain(
            vector_store=vector_store_service.vector_store
        )
        print(f"   RAG链创建成功: {rag_chain is not None}")
        print(f"   向量存储: {rag_chain.vector_store is not None}")
        print(f"   检索器: {rag_chain.retriever is not None}")
        print(f"   LLM服务: {rag_chain.llm_service is not None}")
        
        print("3. 测试简单查询...")
        result = await rag_chain.ainvoke({"query": "你好"})
        print(f"   结果类型: {type(result)}")
        print(f"   结果内容: {result}")
        
        if isinstance(result, dict):
            answer_obj = result.get('answer', '')
            sources = result.get('sources', [])
            # Handle case where answer is an LLMResponse object
            if hasattr(answer_obj, 'content'):
                answer = answer_obj.content
            else:
                answer = str(answer_obj)
        else:
            # Handle LLMResponse object
            try:
                answer = result.content if hasattr(result, 'content') else str(result)
                sources = getattr(result, 'sources', [])
            except:
                answer = str(result)
                sources = []
        print(f"   查询结果: {answer[:100]}...")
        print(f"   使用RAG: {len(sources) > 0}")
        
        print("4. 测试复杂查询...")
        result = await rag_chain.ainvoke({
            "query": "请基于数据合规管理系统的知识库文档,帮我分析下文档的内容并给出分析报告"
        })
        if isinstance(result, dict):
            answer_obj = result.get('answer', '')
            sources = result.get('sources', [])
            # Handle case where answer is an LLMResponse object
            if hasattr(answer_obj, 'content'):
                answer = answer_obj.content
            else:
                answer = str(answer_obj)
        else:
            # Handle LLMResponse object
            try:
                answer = result.content if hasattr(result, 'content') else str(result)
                sources = getattr(result, 'sources', [])
            except:
                answer = str(result)
                sources = []
        print(f"   查询结果: {answer[:200]}...")
        print(f"   使用RAG: {len(sources) > 0}")
        print(f"   源文档数量: {len(sources)}")
        
        print("✅ RAG链测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ RAG链测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_rag_chain())
    sys.exit(0 if success else 1)
