#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""智能工具推荐器测试"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tool_recommender import tool_recommender

def test_tool_recommender():
    """测试智能工具推荐器"""
    print("[TEST] 测试智能工具推荐器...")
    
    # 测试1: 天气查询
    print("测试1: 天气查询 - '北京今天天气怎么样？'")
    result = tool_recommender.recommend_tools("北京今天天气怎么样？")
    assert len(result) > 0, "未推荐任何工具"
    assert result[0]["tool_name"] == "weather", f"推荐工具不正确，实际: {result[0]['tool_name']}"
    print(f"[PASS] 推荐: {result[0]['tool_name']} (置信度: {result[0]['confidence']}%)")
    
    # 测试2: 数学计算
    print("测试2: 数学计算 - '1+2等于多少？'")
    result = tool_recommender.recommend_tools("1+2等于多少？")
    assert result[0]["tool_name"] == "calculate", f"推荐工具不正确，实际: {result[0]['tool_name']}"
    print(f"[PASS] 推荐: {result[0]['tool_name']} (置信度: {result[0]['confidence']}%)")
    
    # 测试3: 时间查询
    print("测试3: 时间查询 - '现在几点了？'")
    result = tool_recommender.recommend_tools("现在几点了？")
    assert result[0]["tool_name"] == "get_current_time", f"推荐工具不正确，实际: {result[0]['tool_name']}"
    print(f"[PASS] 推荐: {result[0]['tool_name']} (置信度: {result[0]['confidence']}%)")
    
    # 测试4: 新闻查询
    print("测试4: 新闻查询 - '今天有什么新闻？'")
    result = tool_recommender.recommend_tools("今天有什么新闻？")
    assert result[0]["tool_name"] == "news", f"推荐工具不正确，实际: {result[0]['tool_name']}"
    print(f"[PASS] 推荐: {result[0]['tool_name']} (置信度: {result[0]['confidence']}%)")
    
    # 测试5: 图片生成
    print("测试5: 图片生成 - '帮我生成一张猫咪图片'")
    result = tool_recommender.recommend_tools("帮我生成一张猫咪图片")
    assert result[0]["tool_name"] == "image", f"推荐工具不正确，实际: {result[0]['tool_name']}"
    print(f"[PASS] 推荐: {result[0]['tool_name']} (置信度: {result[0]['confidence']}%)")
    
    # 测试6: 获取最佳工具
    print("测试6: 获取最佳工具")
    tool = tool_recommender.get_best_tool("上海明天天气")
    assert tool == "weather", f"最佳工具不正确，实际: {tool}"
    print(f"[PASS] 最佳工具: {tool}")
    
    # 测试7: 分析查询
    print("测试7: 分析查询")
    analysis = tool_recommender.analyze_query("计算 1+2")
    assert len(analysis) > 0, "分析结果为空"
    print(f"[PASS] 分析结果数量: {len(analysis)}")
    
    # 测试8: 决策解释
    print("测试8: 决策解释")
    explanation = tool_recommender.explain_decision("北京天气")
    assert "weather" in explanation, "解释不包含正确工具"
    print("[PASS] 决策解释生成成功")
    
    return True

def main():
    """主测试函数"""
    print("="*60)
    print("[INFO] 智能工具推荐器测试")
    print("="*60)
    
    try:
        success = test_tool_recommender()
        
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
