#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据处理工具插件测试"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugins import plugin_manager

def test_data_processor():
    """测试数据处理工具插件"""
    print("[TEST] 测试数据处理工具插件...")
    
    # 加载插件
    try:
        plugin_manager.load_plugin("data_processor_plugin")
        print("[PASS] 插件加载成功")
    except Exception as e:
        print(f"[FAIL] 插件加载失败: {e}")
        return False
    
    # 获取插件
    data_plugin = plugin_manager.get_plugin("data")
    if not data_plugin:
        print("[FAIL] 无法获取 data 插件")
        return False
    
    print("[PASS] 获取插件成功")
    print(f"[INFO] 插件名称: {data_plugin.get_name()}")
    print(f"[INFO] 插件描述: {data_plugin.get_description()}")
    
    # 测试1: 长度单位换算
    print("\n测试1: 长度单位换算")
    result = data_plugin.convert_unit(100, "km", "mile")
    print(f"结果: {result}")
    assert "英里" in result, "转换结果不正确"
    print("[PASS] 长度单位换算测试通过")
    
    # 测试2: 温度换算
    print("\n测试2: 温度换算")
    result = data_plugin.convert_unit(25, "c", "f")
    print(f"结果: {result}")
    assert "华氏度" in result, "转换结果不正确"
    print("[PASS] 温度换算测试通过")
    
    # 测试3: 日期计算 - 获取今天
    print("\n测试3: 日期计算 - 获取今天")
    result = data_plugin.calculate_date("today")
    print(f"结果: {result}")
    assert "今天" in result, "结果不正确"
    print("[PASS] 获取今天日期测试通过")
    
    # 测试4: 日期计算 - 添加天数
    print("\n测试4: 日期计算 - 添加天数")
    result = data_plugin.calculate_date("add", "2024-01-01", 7)
    print(f"结果: {result}")
    assert "01月08日" in result, "日期计算错误"
    print("[PASS] 添加天数测试通过")
    
    # 测试5: 进制转换
    print("\n测试5: 进制转换")
    result = data_plugin.convert_base("1010", 2, 10)
    print(f"结果: {result}")
    assert "10" in result, "进制转换错误"
    print("[PASS] 进制转换测试通过")
    
    # 测试6: 数学计算
    print("\n测试6: 数学计算")
    result = data_plugin.calculate_math("sqrt(16) + 3")
    print(f"结果: {result}")
    assert "7.0" in result or "7" in result, "计算错误"
    print("[PASS] 数学计算测试通过")
    
    # 测试7: 执行命令
    print("\n测试7: 执行命令")
    kwargs = {"value": 100, "from": "kg", "to": "lb"}
    result = data_plugin.execute("convert", **kwargs)
    print(f"结果: {result}")
    assert "磅" in result, "执行失败"
    print("[PASS] 命令执行测试通过")
    
    return True

def main():
    """主测试函数"""
    print("="*60)
    print("[INFO] 数据处理工具插件测试")
    print("="*60)
    
    try:
        success = test_data_processor()
        
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
