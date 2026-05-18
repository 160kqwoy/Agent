#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""记忆管理器测试"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory_manager import memory_manager, MemoryItem

def test_memory_manager():
    """测试记忆管理器"""
    print("[TEST] 测试记忆管理器...")
    
    # 先清空之前的测试数据
    memory_manager.clear_all_memories()
    
    # 测试1: 添加记忆
    print("测试1: 添加记忆")
    memory_id = memory_manager.add_memory(
        "用户喜欢人工智能和机器学习",
        {"user": "test_user", "type": "preference"}
    )
    assert memory_id is not None, "添加记忆失败"
    print(f"[PASS] 测试1通过，记忆ID: {memory_id}")
    
    # 测试2: 获取记忆
    print("测试2: 获取记忆")
    memory = memory_manager.get_memory(memory_id)
    assert memory is not None, "获取记忆失败"
    assert memory.content == "用户喜欢人工智能和机器学习", "记忆内容错误"
    print("[PASS] 测试2通过")
    
    # 测试3: 添加多条记忆
    print("测试3: 添加多条记忆")
    memory_manager.add_memory("用户询问过北京天气", {"user": "test_user", "type": "query"})
    memory_manager.add_memory("用户对Python编程感兴趣", {"user": "test_user", "type": "preference"})
    memory_manager.add_memory("用户使用过计算器工具", {"user": "test_user", "type": "action"})
    print("[PASS] 测试3通过")
    
    # 测试4: 搜索记忆（在删除之前测试）
    print("测试4: 搜索记忆")
    results = memory_manager.search_memories("人工智能")
    assert len(results) > 0, "搜索失败"
    assert any("人工智能" in r.content for r in results), "搜索结果不匹配"
    print(f"[PASS] 测试4通过，找到 {len(results)} 条相关记忆")
    
    # 测试5: 获取最近记忆
    print("测试5: 获取最近记忆")
    recent = memory_manager.get_recent_memories(5)
    assert len(recent) >= 3, "获取最近记忆失败"
    print(f"[PASS] 测试5通过，获取到 {len(recent)} 条记忆")
    
    # 测试6: 获取统计信息
    print("测试6: 获取统计信息")
    stats = memory_manager.get_statistics()
    assert "total_memories" in stats, "统计信息不完整"
    assert stats["total_memories"] >= 3, "记忆数量不正确"
    print(f"[PASS] 测试6通过，总记忆数: {stats['total_memories']}")
    
    # 测试7: 删除记忆
    print("测试7: 删除记忆")
    result = memory_manager.delete_memory(memory_id)
    assert result, "删除记忆失败"
    memory = memory_manager.get_memory(memory_id)
    assert memory is None, "记忆未被删除"
    print("[PASS] 测试7通过")
    
    # 清理测试数据
    memory_manager.clear_all_memories()
    
    return True

def main():
    """主测试函数"""
    print("="*60)
    print("[INFO] 记忆管理器测试")
    print("="*60)
    
    try:
        success = test_memory_manager()
        
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
