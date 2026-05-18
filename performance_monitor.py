#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能监控模块 - API 调用统计、响应时间监控
"""

import time
import functools
from typing import Callable, Any, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PerformanceStats:
    """性能统计数据"""
    
    def __init__(self):
        self.start_time = time.time()
        self.total_calls = 0
        self.success_calls = 0
        self.failed_calls = 0
        self.total_response_time = 0.0
        self.min_response_time = float('inf')
        self.max_response_time = 0.0
        self.response_times: List[float] = []
        self.call_timestamps: List[float] = []
        self.errors: List[Dict[str, Any]] = []
    
    def record_call(self, response_time: float, success: bool = True, error: str = None):
        """记录一次调用"""
        self.total_calls += 1
        self.total_response_time += response_time
        self.response_times.append(response_time)
        self.call_timestamps.append(time.time())
        
        if response_time < self.min_response_time:
            self.min_response_time = response_time
        if response_time > self.max_response_time:
            self.max_response_time = response_time
        
        if success:
            self.success_calls += 1
        else:
            self.failed_calls += 1
            if error:
                self.errors.append({
                    "timestamp": datetime.now().isoformat(),
                    "response_time": response_time,
                    "error": error
                })
    
    @property
    def average_response_time(self) -> float:
        """平均响应时间"""
        if self.total_calls == 0:
            return 0.0
        return self.total_response_time / self.total_calls
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_calls == 0:
            return 0.0
        return (self.success_calls / self.total_calls) * 100
    
    @property
    def p95_response_time(self) -> float:
        """95% 响应时间"""
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        if index >= len(sorted_times):
            index = len(sorted_times) - 1
        return sorted_times[index]
    
    @property
    def p99_response_time(self) -> float:
        """99% 响应时间"""
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.99)
        if index >= len(sorted_times):
            index = len(sorted_times) - 1
        return sorted_times[index]
    
    def get_summary(self) -> Dict[str, Any]:
        """获取统计摘要"""
        return {
            "total_calls": self.total_calls,
            "success_calls": self.success_calls,
            "failed_calls": self.failed_calls,
            "success_rate": f"{self.success_rate:.2f}%",
            "avg_response_time": f"{self.average_response_time:.4f}s",
            "min_response_time": f"{self.min_response_time:.4f}s",
            "max_response_time": f"{self.max_response_time:.4f}s",
            "p95_response_time": f"{self.p95_response_time:.4f}s",
            "p99_response_time": f"{self.p99_response_time:.4f}s",
            "uptime": f"{time.time() - self.start_time:.2f}s"
        }
    
    def reset(self):
        """重置统计数据"""
        self.__init__()

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.stats: Dict[str, PerformanceStats] = {}
        self.global_stats = PerformanceStats()
    
    def get_stats(self, key: str) -> PerformanceStats:
        """获取或创建统计对象"""
        if key not in self.stats:
            self.stats[key] = PerformanceStats()
        return self.stats[key]
    
    def record(self, key: str, response_time: float, success: bool = True, error: str = None):
        """记录调用"""
        self.get_stats(key).record_call(response_time, success, error)
        self.global_stats.record_call(response_time, success, error)
    
    def get_summary(self, key: str = None) -> Dict[str, Any]:
        """获取统计摘要"""
        if key is None:
            return self.global_stats.get_summary()
        return self.get_stats(key).get_summary()
    
    def get_all_summaries(self) -> Dict[str, Dict[str, Any]]:
        """获取所有统计摘要"""
        summaries = {
            "global": self.global_stats.get_summary()
        }
        for key, stats in self.stats.items():
            summaries[key] = stats.get_summary()
        return summaries
    
    def reset(self, key: str = None):
        """重置统计数据"""
        if key is None:
            self.global_stats.reset()
            self.stats = {}
        else:
            if key in self.stats:
                self.stats[key].reset()

# 创建全局性能监控实例
performance_monitor = PerformanceMonitor()

def monitor_performance(key: Optional[str] = None):
    """性能监控装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            func_key = key or func.__name__
            
            try:
                result = func(*args, **kwargs)
                response_time = time.time() - start_time
                
                # 判断是否成功（返回错误字符串视为失败）
                success = not (isinstance(result, str) and result.startswith("错误:"))
                
                # 记录性能数据
                performance_monitor.record(func_key, response_time, success)
                
                return result
            except Exception as e:
                response_time = time.time() - start_time
                performance_monitor.record(func_key, response_time, False, str(e))
                raise
        
        return wrapper
    return decorator

# 便捷函数
def get_performance_summary(key: str = None) -> Dict[str, Any]:
    """获取性能摘要"""
    return performance_monitor.get_summary(key)

def get_all_performance_summaries() -> Dict[str, Dict[str, Any]]:
    """获取所有性能摘要"""
    return performance_monitor.get_all_summaries()

def reset_performance_stats(key: str = None):
    """重置性能统计"""
    performance_monitor.reset(key)