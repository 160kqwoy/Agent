#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误恢复机制 - 自动重试和故障转移
"""

import time
import functools
import random
from typing import Callable, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class RetryConfig:
    """重试配置"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retry_on_exceptions: Tuple = (Exception,),
        retry_on_result: Optional[Callable[[Any], bool]] = None
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retry_on_exceptions = retry_on_exceptions
        self.retry_on_result = retry_on_result

def retry(config: RetryConfig = None):
    """重试装饰器"""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(config.max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # 检查是否需要重试（基于返回结果）
                    if config.retry_on_result and config.retry_on_result(result):
                        raise Exception(f"需要重试: {result}")
                    
                    # 成功
                    if attempt > 0:
                        logger.info(f"重试成功，第 {attempt} 次尝试")
                    return result
                
                except config.retry_on_exceptions as e:
                    last_exception = e
                    
                    if attempt >= config.max_retries:
                        logger.error(f"重试失败，已达最大重试次数 {config.max_retries}")
                        break
                    
                    # 计算延迟（带抖动）
                    if config.jitter:
                        jitter = random.uniform(0, delay * 0.1)
                        wait_time = delay + jitter
                    else:
                        wait_time = delay
                    
                    logger.warning(f"第 {attempt + 1} 次尝试失败: {str(e)}，等待 {wait_time:.2f} 秒后重试")
                    time.sleep(wait_time)
                    
                    # 指数退避
                    delay = min(delay * config.backoff_factor, config.max_delay)
            
            # 如果所有重试都失败，返回最后一次异常或错误结果
            if last_exception:
                # 不抛出异常，而是返回错误消息
                return f"错误: {str(last_exception)}"
            return "错误: 未知错误"
        
        return wrapper
    return decorator

class FailoverManager:
    """故障转移管理器"""
    
    def __init__(self):
        self.fallback_registry = {}
    
    def register_fallback(self, primary_name: str, fallback_func: Callable, priority: int = 1):
        """注册故障转移函数"""
        if primary_name not in self.fallback_registry:
            self.fallback_registry[primary_name] = []
        
        self.fallback_registry[primary_name].append({
            "func": fallback_func,
            "priority": priority
        })
        
        # 按优先级排序
        self.fallback_registry[primary_name].sort(key=lambda x: x["priority"])
    
    def get_fallbacks(self, primary_name: str) -> list:
        """获取故障转移函数列表"""
        return self.fallback_registry.get(primary_name, [])
    
    def execute_with_failover(self, primary_func: Callable, primary_name: str, *args, **kwargs) -> Any:
        """执行函数并在失败时使用故障转移"""
        try:
            result = primary_func(*args, **kwargs)
            
            # 检查是否为错误结果
            if isinstance(result, str) and result.startswith("错误:"):
                raise Exception(result)
            
            return result
        except Exception as e:
            logger.warning(f"主函数 {primary_name} 执行失败: {str(e)}")
            
            # 尝试故障转移
            fallbacks = self.get_fallbacks(primary_name)
            for fallback in fallbacks:
                try:
                    logger.info(f"尝试故障转移到优先级 {fallback['priority']} 的函数")
                    result = fallback["func"](*args, **kwargs)
                    
                    if isinstance(result, str) and result.startswith("错误:"):
                        continue
                    
                    logger.info(f"故障转移成功")
                    return result
                except Exception as fallback_e:
                    logger.warning(f"故障转移失败: {str(fallback_e)}")
            
            # 所有故障转移都失败
            logger.error(f"所有故障转移尝试都失败")
            return f"错误: {str(e)}"

# 创建全局故障转移管理器实例
failover_manager = FailoverManager()

# 便捷函数
def with_retry(max_retries: int = 3, initial_delay: float = 1.0):
    """便捷的重试装饰器"""
    config = RetryConfig(
        max_retries=max_retries,
        initial_delay=initial_delay
    )
    return retry(config)

def register_fallback(primary_name: str, priority: int = 1):
    """便捷的故障转移注册装饰器"""
    def decorator(func: Callable) -> Callable:
        failover_manager.register_fallback(primary_name, func, priority)
        return func
    return decorator

def execute_with_retry_and_failover(
    func: Callable,
    func_name: str = None,
    max_retries: int = 3,
    *args,
    **kwargs
) -> Any:
    """执行函数，支持重试和故障转移"""
    if func_name is None:
        func_name = func.__name__
    
    # 添加重试
    @with_retry(max_retries=max_retries)
    def wrapped_func():
        return func(*args, **kwargs)
    
    # 执行并支持故障转移
    return failover_manager.execute_with_failover(wrapped_func, func_name)