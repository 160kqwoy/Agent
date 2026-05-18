#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文本处理工具插件测试"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugins import plugin_manager

def test_text_processor():
    """测试文本处理工具插件"""
    print("[TEST] 测试文本处理工具插件...")
    
    # 加载插件
    try:
        plugin_manager.load_plugin("text_processor_plugin")
        print("[PASS] 插件加载成功")
    except Exception as e:
        print(f"[FAIL] 插件加载失败: {e}")
        return False
    
    # 获取插件
    text_plugin = plugin_manager.get_plugin("text")
    if not text_plugin:
        print("[FAIL] 无法获取 text 插件")
        return False
    
    print("[PASS] 获取插件成功")
    print(f"[INFO] 插件名称: {text_plugin.get_name()}")
    print(f"[INFO] 插件描述: {text_plugin.get_description()}")
    
    # 测试1: 文本摘要
    print("\n测试1: 文本摘要")
    test_text = "人工智能是计算机科学的一个分支，它致力于研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统。人工智能领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。"
    result = text_plugin.summarize(test_text, max_length=50)
    print(f"原文长度: {len(test_text)}")
    print(f"摘要: {result}")
    assert len(result) <= 55, "摘要长度超过限制"
    print("[PASS] 文本摘要测试通过")
    
    # 测试2: 关键词提取
    print("\n测试2: 关键词提取")
    result = text_plugin.extract_keywords(test_text, top_n=3)
    print(f"关键词: {result}")
    assert "人工智能" in result, "未提取到预期关键词"
    print("[PASS] 关键词提取测试通过")
    
    # 测试3: Markdown转纯文本
    print("\n测试3: Markdown转纯文本")
    md_text = "# 标题\n\n**粗体文本**和*斜体文本*\n\n[链接](https://example.com)"
    result = text_plugin.convert_format(md_text, "markdown", "plain")
    print(f"转换结果: {result}")
    assert "#" not in result, "仍包含Markdown标记"
    assert "*" not in result, "仍包含Markdown标记"
    print("[PASS] Markdown转换测试通过")
    
    # 测试4: HTML转纯文本
    print("\n测试4: HTML转纯文本")
    html_text = "<h1>标题</h1><p>段落内容<br/>换行</p>"
    result = text_plugin.convert_format(html_text, "html", "plain")
    print(f"转换结果: {result}")
    assert "<" not in result, "仍包含HTML标签"
    print("[PASS] HTML转换测试通过")
    
    # 测试5: 拼音转换
    print("\n测试5: 拼音转换")
    result = text_plugin.to_pinyin("你好世界")
    print(f"拼音: {result}")
    assert len(result) > 0, "拼音转换失败"
    print("[PASS] 拼音转换测试通过")
    
    # 测试6: 执行命令
    print("\n测试6: 执行命令")
    result = text_plugin.execute("summarize", text="这是一段测试文本", length=20)
    print(f"执行结果: {result}")
    assert len(result) > 0, "执行失败"
    print("[PASS] 命令执行测试通过")
    
    return True

def main():
    """主测试函数"""
    print("="*60)
    print("[INFO] 文本处理工具插件测试")
    print("="*60)
    
    try:
        success = test_text_processor()
        
        print("\n" + "="*60)
        if success:
            print("[PASS] 所有测试通过！")
        else:
            print("[FAIL] 测试失败！")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
