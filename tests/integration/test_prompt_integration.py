#!/usr/bin/env python3
"""
测试系统提示词集成
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services/main-app'))

from app.chains.compliance_prompts import (
    DATA_COMPLIANCE_EXPERT_PROMPT,
    DEFAULT_COMPLIANCE_CONFIG,
    get_compliance_prompt,
    format_file_context,
    FilePurpose
)


def test_prompt_loading():
    """测试提示词加载"""
    print("=" * 60)
    print("测试提示词加载")
    print("=" * 60)

    # 测试中文提示词
    zh_prompt = get_compliance_prompt(language="zh")
    print(f"✅ 中文提示词长度: {len(zh_prompt)} 字符")

    # 验证关键内容
    assert "数据合规专家" in zh_prompt
    assert "5000字以上" in zh_prompt
    assert "Markdown格式" in zh_prompt
    print("✅ 中文提示词包含所有关键要素")

    # 测试配置
    config = DEFAULT_COMPLIANCE_CONFIG
    print(f"✅ 最小字数要求: {config.min_word_count}")
    print(f"✅ 启用 Emoji: {config.enable_emoji}")
    print(f"✅ 启用 Markdown: {config.enable_markdown}")
    print(f"✅ 仅使用知识库: {config.knowledge_base_only}")


def test_file_context():
    """测试文件上下文格式化"""
    print("\n" + "=" * 60)
    print("测试文件上下文格式化")
    print("=" * 60)

    file_content = "这是一份关于数据出境的合规文档..."
    purpose = FilePurpose.GENERATE_COMPLIANCE_REPORT
    scenario = "跨境数据传输场景"

    context = format_file_context(
        file_content=file_content,
        file_purpose=purpose,
        business_scenario=scenario
    )

    print("格式化后的上下文:")
    print(context)

    assert "📎 附件内容" in context
    assert "📌 处理目的" in context
    assert "💼 业务场景" in context
    print("\n✅ 文件上下文格式化正确")


def test_prompt_template():
    """测试提示词模板"""
    print("\n" + "=" * 60)
    print("测试提示词模板")
    print("=" * 60)

    # 模拟知识库内容和用户输入
    context = "《数据安全法》规定..."
    user_input = "如何进行数据分类分级？"

    # 格式化提示词
    prompt = DATA_COMPLIANCE_EXPERT_PROMPT.format(
        context=context,
        input=user_input,
        file_context=""
    )

    print(f"✅ 格式化后的提示词长度: {len(prompt)} 字符")
    assert context in prompt
    assert user_input in prompt
    print("✅ 提示词模板格式化成功")


def test_response_sections():
    """测试回答章节配置"""
    print("\n" + "=" * 60)
    print("测试回答章节配置")
    print("=" * 60)

    config = DEFAULT_COMPLIANCE_CONFIG

    print("回答章节字数要求:")
    total_words = 0
    for section, word_count in config.response_format.items():
        print(f"  - {section.value}: {word_count} 字")
        total_words += word_count

    print(f"\n✅ 章节总字数: {total_words}")
    print(f"✅ 最小字数要求: {config.min_word_count}")
    assert total_words >= config.min_word_count - 300  # 允许少量差异


def main():
    """运行所有测试"""
    print("\n🚀 开始测试系统提示词集成\n")

    try:
        test_prompt_loading()
        test_file_context()
        test_prompt_template()
        test_response_sections()

        print("\n" + "=" * 60)
        print("✅ 所有测试通过！系统提示词已成功集成")
        print("=" * 60)
        print("\n下一步:")
        print("1. 重启后端服务以加载新的提示词")
        print("2. 测试聊天接口是否返回中文格式的回答")
        print("3. 验证回答是否满足5000字要求")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()