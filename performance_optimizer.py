#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""性能优化模块"""

import time
import hashlib
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
from collections import OrderedDict

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            max_size: 最大缓存条目数
            ttl_seconds: 缓存过期时间（秒）
        """
        self.cache: Dict[str, Dict[str, Any]] = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_str = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self.cache:
            entry = self.cache[key]
            # 检查是否过期
            if datetime.now() < entry['expire_time']:
                self.hits += 1
                # 移动到末尾（LRU）
                self.cache.move_to_end(key)
                return entry['value']
            else:
                # 删除过期缓存
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """设置缓存值"""
        # 如果缓存已满，删除最旧的条目（LRU）
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        expire_time = datetime.now() + timedelta(seconds=ttl_seconds or self.ttl_seconds)
        self.cache[key] = {
            'value': value,
            'expire_time': expire_time,
            'created_at': datetime.now()
        }
    
    def delete(self, key: str):
        """删除缓存"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        hit_rate = (self.hits / (self.hits + self.misses)) * 100 if (self.hits + self.misses) > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'size': len(self.cache),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl_seconds
        }
    
    def cached(self, ttl_seconds: Optional[int] = None):
        """装饰器：缓存函数结果"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, *args, **kwargs)
                cached_value = self.get(key)
                
                if cached_value is not None:
                    return cached_value
                
                result = func(*args, **kwargs)
                self.set(key, result, ttl_seconds)
                return result
            
            return wrapper
        return decorator

class AsyncCacheManager(CacheManager):
    """异步缓存管理器"""
    
    async def get_async(self, key: str) -> Optional[Any]:
        """异步获取缓存值"""
        return self.get(key)
    
    async def set_async(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """异步设置缓存值"""
        self.set(key, value, ttl_seconds)
    
    def cached_async(self, ttl_seconds: Optional[int] = None):
        """装饰器：异步缓存函数结果"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, *args, **kwargs)
                cached_value = await self.get_async(key)
                
                if cached_value is not None:
                    return cached_value
                
                result = await func(*args, **kwargs)
                await self.set_async(key, result, ttl_seconds)
                return result
            
            return wrapper
        return decorator

class RateLimiter:
    """请求限流器"""
    
    def __init__(self, max_requests: int, time_window_seconds: int = 60):
        """
        初始化限流器
        
        Args:
            max_requests: 时间窗口内最大请求数
            time_window_seconds: 时间窗口大小（秒）
        """
        self.max_requests = max_requests
        self.time_window = timedelta(seconds=time_window_seconds)
        self.requests: Dict[str, list] = {}  # key -> [timestamps]
    
    def is_allowed(self, key: str = "default") -> bool:
        """检查是否允许请求"""
        now = datetime.now()
        
        # 清理过期请求记录
        if key in self.requests:
            self.requests[key] = [
                ts for ts in self.requests[key]
                if now - ts < self.time_window
            ]
        
        # 检查是否超过限制
        if len(self.requests.get(key, [])) >= self.max_requests:
            return False
        
        # 记录请求时间
        if key not in self.requests:
            self.requests[key] = []
        self.requests[key].append(now)
        return True
    
    def get_remaining(self, key: str = "default") -> int:
        """获取剩余请求数"""
        now = datetime.now()
        
        if key in self.requests:
            self.requests[key] = [
                ts for ts in self.requests[key]
                if now - ts < self.time_window
            ]
        
        return max(0, self.max_requests - len(self.requests.get(key, [])))
    
    def reset(self, key: str = "default"):
        """重置指定key的请求计数"""
        if key in self.requests:
            self.requests[key] = []

class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self, max_concurrent_tasks: int = 10):
        """
        初始化任务管理器
        
        Args:
            max_concurrent_tasks: 最大并发任务数
        """
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.tasks: Dict[str, asyncio.Task] = {}
        self.results: Dict[str, Any] = {}
    
    async def run_task(self, task_id: str, coro, timeout: int = 30) -> Any:
        """
        运行异步任务
        
        Args:
            task_id: 任务ID
            coro: 协程对象
            timeout: 超时时间（秒）
        
        Returns:
            任务结果
        """
        async with self.semaphore:
            try:
                result = await asyncio.wait_for(coro, timeout=timeout)
                self.results[task_id] = {'result': result, 'status': 'success'}
                return result
            except asyncio.TimeoutError:
                self.results[task_id] = {'result': None, 'status': 'timeout'}
                raise
            except Exception as e:
                self.results[task_id] = {'result': str(e), 'status': 'error'}
                raise
    
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务结果"""
        return self.results.get(task_id)
    
    def cancel_task(self, task_id: str):
        """取消任务"""
        if task_id in self.tasks:
            self.tasks[task_id].cancel()
            del self.tasks[task_id]
    
    def get_active_tasks_count(self) -> int:
        """获取活跃任务数"""
        return sum(1 for task in self.tasks.values() if not task.done())

class PerformanceTimer:
    """性能计时器"""
    
    def __init__(self):
        self.timers: Dict[str, list] = {}
    
    def start(self, name: str):
        """开始计时"""
        if name not in self.timers:
            self.timers[name] = []
        self.timers[name].append({'start': time.time()})
    
    def stop(self, name: str) -> float:
        """停止计时并返回耗时（秒）"""
        if name not in self.timers or not self.timers[name]:
            return 0.0
        
        last_timer = self.timers[name][-1]
        last_timer['end'] = time.time()
        elapsed = last_timer['end'] - last_timer['start']
        return elapsed
    
    def get_stats(self, name: str) -> Dict[str, float]:
        """获取计时统计"""
        if name not in self.timers:
            return {'count': 0, 'avg': 0.0, 'min': 0.0, 'max': 0.0, 'total': 0.0}
        
        durations = []
        for timer in self.timers[name]:
            if 'end' in timer:
                durations.append(timer['end'] - timer['start'])
        
        if not durations:
            return {'count': 0, 'avg': 0.0, 'min': 0.0, 'max': 0.0, 'total': 0.0}
        
        return {
            'count': len(durations),
            'avg': sum(durations) / len(durations),
            'min': min(durations),
            'max': max(durations),
            'total': sum(durations)
        }
    
    def timed(self, name: Optional[str] = None):
        """装饰器：计时函数执行时间"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                timer_name = name or func.__name__
                self.start(timer_name)
                try:
                    return func(*args, **kwargs)
                finally:
                    elapsed = self.stop(timer_name)
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                timer_name = name or func.__name__
                self.start(timer_name)
                try:
                    return await func(*args, **kwargs)
                finally:
                    elapsed = self.stop(timer_name)
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return wrapper
        return decorator

# 创建全局实例
cache_manager = CacheManager(max_size=1000, ttl_seconds=3600)
async_cache_manager = AsyncCacheManager(max_size=1000, ttl_seconds=3600)
rate_limiter = RateLimiter(max_requests=100, time_window_seconds=60)
task_manager = AsyncTaskManager(max_concurrent_tasks=10)
performance_timer = PerformanceTimer()

# 便捷函数
def cached(ttl_seconds: Optional[int] = None):
    """缓存装饰器"""
    return cache_manager.cached(ttl_seconds)

def cached_async(ttl_seconds: Optional[int] = None):
    """异步缓存装饰器"""
    return async_cache_manager.cached_async(ttl_seconds)

def timed(name: Optional[str] = None):
    """计时装饰器"""
    return performance_timer.timed(name)

def is_request_allowed(key: str = "default") -> bool:
    """检查请求是否被允许"""
    return rate_limiter.is_allowed(key)

def get_performance_summary() -> Dict[str, Any]:
    """获取性能摘要"""
    return {
        'cache': cache_manager.get_stats(),
        'rate_limiter': {
            'max_requests': rate_limiter.max_requests,
            'remaining': rate_limiter.get_remaining()
        },
        'active_tasks': task_manager.get_active_tasks_count(),
        'timers': {name: performance_timer.get_stats(name) for name in performance_timer.timers}
    }

# 示例用法
if __name__ == "__main__":
    # 示例1: 使用缓存装饰器
    @cached(ttl_seconds=60)
    def expensive_calculation(x, y):
        time.sleep(1)  # 模拟耗时计算
        return x + y
    
    # 示例2: 使用计时装饰器
    @timed("calculation")
    def another_function():
        time.sleep(0.5)
        return "done"
    
    # 测试缓存
    print("第一次调用（应该缓存）:")
    start = time.time()
    result = expensive_calculation(1, 2)
    print(f"结果: {result}, 耗时: {time.time() - start:.2f}s")
    
    print("\n第二次调用（应该命中缓存）:")
    start = time.time()
    result = expensive_calculation(1, 2)
    print(f"结果: {result}, 耗时: {time.time() - start:.2f}s")
    
    # 测试限流
    print("\n测试限流:")
    for i in range(5):
        allowed = rate_limiter.is_allowed("test")
        print(f"请求 {i+1}: {'允许' if allowed else '拒绝'}")
    
    # 输出性能摘要
    print("\n性能摘要:")
    summary = get_performance_summary()
    print(f"缓存命中率: {summary['cache']['hit_rate']}%")
    print(f"剩余请求数: {summary['rate_limiter']['remaining']}")
