#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对话上下文管理器测试"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from context_manager import context_manager, update_conversation_context, get_conversation_context, resolve_references_in_text, get_conversation_summary

def test_context_manager():
    """测试对话上下文管理器"""
    print("[TEST] 测试对话上下文管理器...")
    conversation_id = "test_conversation"
    
    # 测试1: 添加消息
    print("测试1: 添加消息到上下文")
    update_conversation_context(conversation_id, "user", "北京今天天气怎么样？")
    update_conversation_context(conversation_id, "assistant", "北京今天晴朗，气温25度。")
    context = get_conversation_context(conversation_id)
    assert "北京" in context, "上下文不包含地点信息"
    print("[PASS] 添加消息测试通过")
    
    # 测试2: 实体识别
    print("\n测试2: 实体识别")
    entities = context_manager.extract_entities("北京明天天气")
    assert "北京" in entities["locations"], "未识别到地点"
    assert "明天" in entities["dates"], "未识别到日期"
    print(f"[PASS] 实体识别结果: {entities}")
    
    # 测试3: 意图识别
    print("\n测试3: 意图识别")
    intent = context_manager.recognize_intent("帮我计算 1+1")
    assert "calculation" in intent, "未识别到计算意图"
    print(f"[PASS] 意图识别结果: {intent}")
    
    # 测试4: 指代解析
    print("\n测试4: 指代解析")
    # 先添加上下文
    update_conversation_context(conversation_id, "user", "上海")
    result = resolve_references_in_text(conversation_id, "那里的天气怎么样？")
    print(f"解析前: 那里的天气怎么样？")
    print(f"解析后: {result}")
    assert "上海" in result or "北京" in result, "指代解析失败"
    print("[PASS] 指代解析测试通过")
    
    # 测试5: 话题推断
    print("\n测试5: 话题推断")
    topic = context_manager.infer_topic(conversation_id)
    assert topic in ["weather_query", "general"], f"话题推断错误: {topic}"
    print(f"[PASS] 当前话题: {topic}")
    
    # 测试6: 上下文摘要
    print("\n测试6: 上下文摘要")
    summary = get_conversation_summary(conversation_id)
    assert "讨论地点" in summary or "当前话题" in summary, "摘要生成失败"
    print(f"[PASS] 摘要: {summary}")
    
    # 测试7: 清空上下文
    print("\n测试7: 清空上下文")
    context_manager.clear_context(conversation_id)
    context = get_conversation_context(conversation_id)
    assert context == "", "上下文未清空"
    print("[PASS] 清空上下文测试通过")
    
    return True

def test_intent_recognition():
    """测试意图识别"""
    print("\n[TEST] 测试意图识别...")
    
    test_cases = [
        ("北京今天天气怎么样？", "weather_query"),
        ("今天有什么新闻？", "news_query"),
        ("计算 100+200", "calculation"),
        ("现在几点了？", "time_query"),
        ("帮我生成一张图片", "image_generation"),
        ("帮我总结这段文字", "text_processing"),
        ("公斤和磅怎么换算？", "data_conversion"),
        ("你还记得我之前说的话吗", "memory_access"),
        ("你好", "general_chat")
    ]
    
    for text, expected_intent in test_cases:
        intent = context_manager.recognize_intent(text)
        if intent:
            top_intent = next(iter(intent))
            print(f"输入: {text}")
            print(f"识别意图: {top_intent} (置信度: {intent[top_intent]}%)")
            assert top_intent == expected_intent, f"意图识别错误: 期望 {expected_intent}, 实际 {top_intent}"
        else:
            print(f"输入: {text} - 未识别到意图")
        print()
    
    print("[PASS] 意图识别测试通过")
    return True

def test_entity_extraction():
    """测试实体提取"""
    print("\n[TEST] 测试实体提取...")
    
    text = "北京明天温度是多少？帮我计算 100+200"
    entities = context_manager.extract_entities(text)
    
    print(f"输入文本: {text}")
    print(f"提取的实体:")
    print(f"  地点: {entities['locations']}")
    print(f"  日期: {entities['dates']}")
    print(f"  数字: {entities['numbers']}")
    print(f"  话题: {entities['topics']}")
    
    assert "北京" in entities["locations"], "未提取到地点"
    assert "明天" in entities["dates"], "未提取到日期"
    assert "100" in entities["numbers"], "未提取到数字"
    assert "weather" in entities["topics"], "未提取到话题"
    
    print("[PASS] 实体提取测试通过")
    return True

def main():
    """主测试函数"""
    print("="*60)
    print("[INFO] 对话上下文管理器测试")
    print("="*60)
    
    try:
        success = True
        
        success &= test_context_manager()
        success &= test_intent_recognition()
        success &= test_entity_extraction()
        
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
