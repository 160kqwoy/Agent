# 改进11：性能优化

## 概述

为 AI Agent 系统添加了性能优化模块，包含缓存机制、请求限流、异步任务管理和性能计时功能。

## 功能特性

### 1. 缓存管理器
- **LRU缓存策略**：自动淘汰最久未使用的缓存
- **TTL过期机制**：支持自定义过期时间
- **缓存统计**：命中率、命中/未命中次数统计
- **装饰器支持**：方便地为函数添加缓存功能

### 2. 请求限流器
- **滑动窗口限流**：基于时间窗口的请求计数
- **多Key支持**：支持按用户/IP等维度限流
- **剩余请求查询**：实时获取剩余请求配额

### 3. 异步任务管理
- **并发控制**：限制最大并发任务数
- **超时处理**：支持任务超时设置
- **任务追踪**：跟踪任务状态和结果

### 4. 性能计时器
- **函数计时**：装饰器方式记录函数执行时间
- **统计分析**：平均耗时、最小/最大耗时、总耗时
- **多计时器支持**：同时跟踪多个函数

## 文件结构

```
performance_optimizer.py    # 性能优化模块
```

## 使用方法

### 缓存装饰器

```python
from performance_optimizer import cached, timed

# 缓存函数结果，60秒过期
@cached(ttl_seconds=60)
def expensive_api_call(param1, param2):
    # 耗时操作
    return result

# 第一次调用会执行并缓存
result1 = expensive_api_call("a", "b")

# 第二次调用直接返回缓存结果
result2 = expensive_api_call("a", "b")
```

### 性能计时

```python
@timed("api_call")
def my_function():
    # 代码逻辑
    pass

# 获取计时统计
stats = performance_timer.get_stats("api_call")
print(f"调用次数: {stats['count']}")
print(f"平均耗时: {stats['avg']:.4f}s")
```

### 请求限流

```python
from performance_optimizer import is_request_allowed

def handle_request(user_id):
    if not is_request_allowed(user_id):
        return "请求过于频繁，请稍后重试"
    
    # 处理请求
    return process_request()
```

### 异步任务管理

```python
from performance_optimizer import task_manager

async def background_task():
    # 后台任务逻辑
    await asyncio.sleep(1)
    return "done"

# 运行异步任务
result = await task_manager.run_task("task_id", background_task())
```

### 获取性能摘要

```python
from performance_optimizer import get_performance_summary

summary = get_performance_summary()
print(f"缓存命中率: {summary['cache']['hit_rate']}%")
print(f"剩余请求数: {summary['rate_limiter']['remaining']}")
print(f"活跃任务数: {summary['active_tasks']}")
```

## 测试结果

```
[INFO] 性能优化模块测试
============================================================
[TEST] 测试缓存管理器...
测试1: 设置和获取缓存 [PASS]
测试2: 缓存命中率统计 [PASS] - 命中=1, 未命中=0
测试3: 缓存过期 [PASS]
测试4: 缓存装饰器 [PASS] - 函数调用次数: 1
测试5: LRU淘汰机制 [PASS]

[TEST] 测试限流器...
测试1: 正常请求 [PASS]
测试2: 超过限制 [PASS]
测试3: 剩余请求数 [PASS] - 100

[TEST] 测试性能计时器...
测试1: 基本计时 [PASS] - 0.1004s
测试2: 计时装饰器 [PASS] - 调用次数=1, 平均耗时=0.0504s

[TEST] 测试性能摘要...
[PASS] 缓存命中率: 60.0%
[PASS] 剩余请求数: 100
[PASS] 活跃任务数: 0

============================================================
[PASS] 所有测试通过！
```

## 配置参数

### 缓存管理器
| 参数 | 默认值 | 说明 |
|------|--------|------|
| max_size | 1000 | 最大缓存条目数 |
| ttl_seconds | 3600 | 默认过期时间（秒） |

### 请求限流器
| 参数 | 默认值 | 说明 |
|------|--------|------|
| max_requests | 100 | 时间窗口内最大请求数 |
| time_window_seconds | 60 | 时间窗口大小（秒） |

### 异步任务管理器
| 参数 | 默认值 | 说明 |
|------|--------|------|
| max_concurrent_tasks | 10 | 最大并发任务数 |

## 注意事项

1. **缓存键生成**：基于函数名和参数生成MD5哈希
2. **缓存过期**：过期缓存会在获取时自动清理
3. **限流时间窗口**：使用滑动窗口算法，精确控制请求频率
4. **异步任务超时**：默认超时30秒，可自定义

## 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-18 | 初始版本 |
