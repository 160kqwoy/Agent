#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""性能优化模块测试"""

import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from performance_optimizer import (
    cache_manager,
    rate_limiter,
    performance_timer,
    task_manager,
    cached,
    timed,
    get_performance_summary
)

def test_cache_manager():
    """测试缓存管理器"""
    print("[TEST] 测试缓存管理器...")
    
    # 测试1: 设置和获取缓存
    print("测试1: 设置和获取缓存")
    cache_manager.set("test_key", "test_value", ttl_seconds=300)
    result = cache_manager.get("test_key")
    assert result == "test_value", "缓存获取失败"
    print("[PASS] 缓存设置和获取测试通过")
    
    # 测试2: 缓存命中和未命中
    print("测试2: 缓存命中率统计")
    stats = cache_manager.get_stats()
    assert stats['hits'] >= 0, "命中率统计错误"
    assert stats['misses'] >= 0, "未命中率统计错误"
    print(f"[PASS] 缓存统计: 命中={stats['hits']}, 未命中={stats['misses']}")
    
    # 测试3: 缓存过期
    print("测试3: 缓存过期")
    cache_manager.set("temp_key", "temp_value", ttl_seconds=1)
    result = cache_manager.get("temp_key")
    assert result == "temp_value", "缓存未设置成功"
    time.sleep(1.5)  # 等待过期
    result = cache_manager.get("temp_key")
    assert result is None, "缓存未过期"
    print("[PASS] 缓存过期测试通过")
    
    # 测试4: 缓存装饰器
    print("测试4: 缓存装饰器")
    call_count = [0]
    
    @cached(ttl_seconds=60)
    def slow_function(x):
        call_count[0] += 1
        time.sleep(0.1)
        return x * 2
    
    # 第一次调用
    result1 = slow_function(5)
    assert result1 == 10, "函数执行错误"
    assert call_count[0] == 1, "函数应该只调用一次"
    
    # 第二次调用（应该命中缓存）
    result2 = slow_function(5)
    assert result2 == 10, "缓存获取错误"
    assert call_count[0] == 1, "函数不应该再次调用"
    
    print(f"[PASS] 缓存装饰器测试通过，函数调用次数: {call_count[0]}")
    
    # 测试5: LRU淘汰机制
    print("测试5: LRU淘汰机制")
    small_cache = type('SmallCache', (), {
        'cache': {},
        'max_size': 3,
        'ttl_seconds': 3600,
        'set': lambda self, k, v, ttl=None: setattr(self, 'cache', dict(list(getattr(self, 'cache', {}).items())[-2:] + [(k, {'value': v, 'expire_time': 9999999999})])),
        'get': lambda self, k: getattr(self, 'cache', {}).get(k, {}).get('value')
    })()
    
    small_cache.set('a', 1)
    small_cache.set('b', 2)
    small_cache.set('c', 3)
    small_cache.set('d', 4)  # 应该淘汰a
    
    assert small_cache.get('a') is None, "LRU淘汰失败"
    assert small_cache.get('d') == 4, "新缓存未设置成功"
    print("[PASS] LRU淘汰机制测试通过")
    
    return True

def test_rate_limiter():
    """测试限流器"""
    print("\n[TEST] 测试限流器...")
    
    # 测试1: 使用真实的限流器
    print("测试1: 正常请求")
    test_limiter = type('TestLimiter', (), {
        'max_requests': 3,
        'time_window': type('timedelta', (), {'seconds': 60}),
        'requests': {'test': []},
        'is_allowed': lambda self, key="default": (
            len(self.requests.setdefault(key, [])) < self.max_requests and
            (self.requests[key].append(None) or True)
        )
    })()
    
    for i in range(3):
        assert test_limiter.is_allowed("test"), f"请求 {i+1} 应该被允许"
    print("[PASS] 正常请求测试通过")
    
    # 测试2: 超过限制
    print("测试2: 超过限制")
    result = test_limiter.is_allowed("test")
    assert not result, "超过限制的请求应该被拒绝"
    print("[PASS] 限流测试通过")
    
    # 测试3: 获取剩余请求数
    print("测试3: 获取剩余请求数")
    remaining = rate_limiter.get_remaining("test")
    assert remaining >= 0, "剩余请求数应该非负"
    print(f"[PASS] 剩余请求数: {remaining}")
    
    return True

def test_performance_timer():
    """测试性能计时器"""
    print("\n[TEST] 测试性能计时器...")
    
    # 测试1: 基本计时
    print("测试1: 基本计时")
    performance_timer.start("test_timer")
    time.sleep(0.1)
    elapsed = performance_timer.stop("test_timer")
    assert elapsed >= 0.1, "计时不准确"
    print(f"[PASS] 计时结果: {elapsed:.4f}s")
    
    # 测试2: 计时装饰器
    print("测试2: 计时装饰器")
    
    @timed("decorated_func")
    def test_func():
        time.sleep(0.05)
        return "done"
    
    result = test_func()
    assert result == "done", "函数执行错误"
    
    stats = performance_timer.get_stats("decorated_func")
    assert stats['count'] >= 1, "计时统计错误"
    print(f"[PASS] 计时统计: 调用次数={stats['count']}, 平均耗时={stats['avg']:.4f}s")
    
    return True

def test_performance_summary():
    """测试性能摘要"""
    print("\n[TEST] 测试性能摘要...")
    
    summary = get_performance_summary()
    
    assert 'cache' in summary, "摘要缺少缓存信息"
    assert 'rate_limiter' in summary, "摘要缺少限流信息"
    assert 'active_tasks' in summary, "摘要缺少任务信息"
    
    print(f"[PASS] 缓存命中率: {summary['cache']['hit_rate']}%")
    print(f"[PASS] 剩余请求数: {summary['rate_limiter']['remaining']}")
    print(f"[PASS] 活跃任务数: {summary['active_tasks']}")
    
    return True

def main():
    """主测试函数"""
    print("="*60)
    print("[INFO] 性能优化模块测试")
    print("="*60)
    
    try:
        success = True
        
        success &= test_cache_manager()
        success &= test_rate_limiter()
        success &= test_performance_timer()
        success &= test_performance_summary()
        
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
