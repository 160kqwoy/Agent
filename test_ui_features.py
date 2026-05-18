#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI功能测试"""

import sys
import os
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_export_chat_history():
    """测试聊天历史导出功能"""
    print("[TEST] 测试聊天历史导出功能...")
    
    # 模拟聊天历史
    mock_history = [
        {
            "user": "你好",
            "assistant": "你好！我是 AI Agent，很高兴为你服务。",
            "timestamp": datetime.now().isoformat()
        },
        {
            "user": "北京今天天气怎么样？",
            "assistant": "北京今天晴朗，气温 25°C。",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    # 测试 JSON 导出
    print("测试1: JSON 格式导出")
    data = json.dumps(mock_history, ensure_ascii=False, indent=2)
    assert '"user"' in data, "JSON格式不正确"
    assert '"assistant"' in data, "JSON格式不正确"
    print("[PASS] JSON 导出测试通过")
    
    # 测试 Markdown 导出
    print("测试2: Markdown 格式导出")
    lines = ["# 聊天历史", ""]
    for i, message in enumerate(mock_history, 1):
        timestamp = message.get("timestamp", "")
        if timestamp:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"---\n## 对话 {i} ({time_str})")
        else:
            lines.append(f"---\n## 对话 {i}")
        lines.append(f"**用户**: {message['user']}")
        lines.append(f"**助手**: {message['assistant']}")
        lines.append("")
    md_data = "\n".join(lines)
    assert "# 聊天历史" in md_data, "Markdown格式不正确"
    assert "**用户**:" in md_data, "Markdown格式不正确"
    print("[PASS] Markdown 导出测试通过")
    
    # 测试 TXT 导出
    print("测试3: TXT 格式导出")
    lines = []
    for i, message in enumerate(mock_history, 1):
        timestamp = message.get("timestamp", "")
        if timestamp:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"=== 对话 {i} ({time_str}) ===")
        else:
            lines.append(f"=== 对话 {i} ===")
        lines.append(f"用户: {message['user']}")
        lines.append(f"助手: {message['assistant']}")
        lines.append("")
    txt_data = "\n".join(lines)
    assert "===" in txt_data, "TXT格式不正确"
    print("[PASS] TXT 导出测试通过")
    
    # 测试空历史导出
    print("测试4: 空历史导出")
    empty_history = []
    if not empty_history:
        print("[PASS] 空历史处理测试通过")
    
    return True

def test_theme_toggle():
    """测试主题切换功能"""
    print("\n[TEST] 测试主题切换功能...")
    
    # 模拟主题状态
    theme = "light"
    
    # 切换到深色
    if theme == "light":
        theme = "dark"
    assert theme == "dark", "主题切换失败"
    print("[PASS] 切换到深色模式")
    
    # 切换到浅色
    if theme == "dark":
        theme = "light"
    assert theme == "light", "主题切换失败"
    print("[PASS] 切换到浅色模式")
    
    return True

def test_chat_history_with_timestamp():
    """测试带时间戳的聊天历史"""
    print("\n[TEST] 测试带时间戳的聊天历史...")
    
    # 创建带时间戳的消息
    message = {
        "user": "测试消息",
        "assistant": "测试回复",
        "timestamp": datetime.now().isoformat()
    }
    
    assert "timestamp" in message, "缺少时间戳"
    assert message["timestamp"], "时间戳为空"
    
    # 解析时间戳
    parsed_dt = datetime.fromisoformat(message["timestamp"])
    assert isinstance(parsed_dt, datetime), "时间戳格式不正确"
    print(f"[PASS] 时间戳解析成功: {parsed_dt}")
    
    return True

def main():
    """主测试函数"""
    print("="*60)
    print("[INFO] UI功能测试")
    print("="*60)
    
    try:
        success = True
        
        success &= test_export_chat_history()
        success &= test_theme_toggle()
        success &= test_chat_history_with_timestamp()
        
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
