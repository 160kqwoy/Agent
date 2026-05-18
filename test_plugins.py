#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：插件化架构
"""

import os
import sys

# 设置输出编码
sys.stdout.reconfigure(encoding='utf-8')

# 添加主模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugins import (
    plugin_manager,
    load_plugins,
    get_tools_from_plugins,
    reload_plugin,
    Plugin,
    ToolPlugin
)

from main import load_plugins_and_tools

def test_plugins():
    """测试插件化架构"""
    print("=" * 60)
    print("测试插件化架构")
    print("=" * 60)
    
    # 测试1：加载插件
    print("\n[测试1] 加载插件")
    plugins = load_plugins()
    print(f"已加载插件: {plugins}")
    assert len(plugins) > 0, "未加载任何插件"
    print("[PASS] 测试1通过")
    
    # 测试2：获取工具列表
    print("\n[测试2] 获取工具列表")
    tools = get_tools_from_plugins()
    print(f"工具数量: {len(tools)}")
    assert len(tools) > 0, "工具列表为空"
    print("[PASS] 测试2通过")
    
    # 测试3：检查时间工具
    print("\n[测试3] 检查时间工具")
    time_plugin = plugin_manager.get_plugin("get_current_time")
    assert time_plugin is not None, "时间插件未加载"
    result = time_plugin.execute()
    assert "当前时间" in result, "时间工具执行失败"
    print(f"[PASS] 测试3通过 - {result[:30]}...")
    
    # 测试4：检查计算器工具
    print("\n[测试4] 检查计算器工具")
    calc_plugin = plugin_manager.get_plugin("calculate")
    assert calc_plugin is not None, "计算器插件未加载"
    result = calc_plugin.execute("2+3")
    assert "5" in result, "计算器工具执行失败"
    print(f"[PASS] 测试4通过 - {result}")
    
    # 测试5：检查文件操作工具
    print("\n[测试5] 检查文件操作工具")
    file_plugin = plugin_manager.get_plugin("file_operations")
    assert file_plugin is not None, "文件操作插件未加载"
    # 测试写入文件
    result = file_plugin.execute("write", "test_plugin.txt", "hello")
    assert "写入成功" in result, "文件写入失败"
    print(f"[PASS] 测试5通过 - {result}")
    
    # 测试6：检查搜索工具
    print("\n[测试6] 检查搜索工具")
    search_plugin = plugin_manager.get_plugin("web_search")
    assert search_plugin is not None, "搜索插件未加载"
    print("[PASS] 测试6通过")
    
    # 测试7：主程序工具加载
    print("\n[测试7] 主程序工具加载")
    tool_count = load_plugins_and_tools()
    assert tool_count >= 4, f"工具加载不足: {tool_count}"
    print(f"[PASS] 测试7通过 - 已加载 {tool_count} 个工具")
    
    # 测试8：检查工具列表内容
    print("\n[测试8] 检查工具列表内容")
    tools = get_tools_from_plugins()
    assert "get_current_time" in tools, "时间工具未在工具列表中"
    assert "calculate" in tools, "计算器工具未在工具列表中"
    print("[PASS] 测试8通过")
    
    # 测试9：插件热更新
    print("\n[测试9] 插件热更新")
    original_count = len(get_tools_from_plugins())
    refreshed_plugin = plugin_manager.reload_plugin("time_plugin")
    assert refreshed_plugin is not None, "热更新失败"
    # 重新加载工具列表
    load_plugins_and_tools()
    new_count = len(get_tools_from_plugins())
    assert original_count == new_count, "热更新后工具数量变化"
    # 验证热更新后的插件仍然可用
    time_plugin = plugin_manager.get_plugin("get_current_time")
    result = time_plugin.execute()
    assert "当前时间" in result, "热更新后时间工具不可用"
    print("[PASS] 测试9通过")
    
    # 清理测试文件
    if os.path.exists("test_plugin.txt"):
        os.remove("test_plugin.txt")
    
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)

if __name__ == "__main__":
    test_plugins()
