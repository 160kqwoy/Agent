# 改进10：对话上下文增强

## 概述

为 AI Agent 系统添加了对话上下文管理器，实现多轮对话记忆、意图识别、实体提取和指代解析功能。

## 功能特性

### 1. 对话上下文管理
- 多会话支持（按 conversation_id 区分）
- 消息历史记录（自动限制长度）
- 格式化上下文输出

### 2. 实体识别与缓存
- 地点实体识别
- 日期实体识别
- 数字实体识别
- 话题实体识别
- 实体缓存机制

### 3. 意图识别
- 支持多种意图类型：
  - weather_query（天气查询）
  - news_query（新闻查询）
  - calculation（数学计算）
  - time_query（时间查询）
  - image_generation（图片生成）
  - text_processing（文本处理）
  - data_conversion（数据转换）
  - memory_access（记忆访问）
  - general_chat（通用聊天）
- 置信度评估
- 意图历史跟踪

### 4. 话题跟踪
- 自动推断当前话题
- 话题变化检测
- 话题置信度评估

### 5. 指代解析
- 解析"它"、"这个"、"那里"等指代词
- 自动替换为具体内容

### 6. 上下文摘要
- 自动生成对话摘要
- 包含实体、意图、话题信息

## 文件结构

```
context_manager.py    # 对话上下文管理器
```

## 使用方法

### 基本使用

```python
from context_manager import (
    context_manager,
    update_conversation_context,
    get_conversation_context,
    resolve_references_in_text,
    get_conversation_summary
)

# 对话ID
conversation_id = "user_123"

# 添加对话消息
update_conversation_context(conversation_id, "user", "北京今天天气怎么样？")
update_conversation_context(conversation_id, "assistant", "北京今天晴朗，气温25度。")

# 获取上下文
context = get_conversation_context(conversation_id)
print(context)

# 解析指代
resolved = resolve_references_in_text(conversation_id, "那里的天气怎么样？")
print(resolved)  # 输出: 北京的天气怎么样？

# 获取对话摘要
summary = get_conversation_summary(conversation_id)
print(summary)
```

### 意图识别

```python
# 识别意图
intent = context_manager.recognize_intent("帮我计算 1+1")
print(intent)  # {'calculation': 28.57}

# 跟踪意图
context_manager.track_intent(conversation_id, "帮我计算 1+1")

# 获取当前意图
current_intent = context_manager.get_current_intent(conversation_id)
print(current_intent)  # calculation
```

### 实体提取

```python
# 提取实体
entities = context_manager.extract_entities("北京明天温度是多少？")
print(entities)
# {'locations': ['北京'], 'dates': ['明天'], 'numbers': [], 'topics': ['weather']}

# 获取最近地点
location = context_manager.get_recent_location(conversation_id)
print(location)  # 北京
```

### 话题跟踪

```python
# 推断话题
topic = context_manager.infer_topic(conversation_id)
print(topic)  # weather_query

# 检测话题变化
changed = context_manager.detect_topic_change(conversation_id, "今天有什么新闻？")
print(changed)  # True
```

## 测试结果

```
[INFO] 对话上下文管理器测试
============================================================
[TEST] 测试对话上下文管理器...
测试1: 添加消息 [PASS]
测试2: 实体识别 [PASS]
测试3: 意图识别 [PASS]
测试4: 指代解析 [PASS] - "那里" → "上海"
测试5: 话题推断 [PASS] - weather_query
测试6: 上下文摘要 [PASS]
测试7: 清空上下文 [PASS]

[TEST] 测试意图识别...
输入: 北京今天天气怎么样？ → weather_query (28.57%)
输入: 今天有什么新闻？ → news_query (30.0%)
输入: 计算 100+200 → calculation (28.57%)
输入: 现在几点了？ → time_query (80.0%)
输入: 帮我生成一张图片 → image_generation (75.0%)
输入: 帮我总结这段文字 → text_processing (30.0%)
输入: 公斤和磅怎么换算？ → data_conversion (37.5%)
输入: 你还记得我之前说的话吗 → memory_access (50.0%)
输入: 你好 → general_chat (20.0%)

[TEST] 测试实体提取...
输入: 北京明天温度是多少？帮我计算 100+200
输出: 地点: ['北京'], 日期: ['明天'], 数字: ['100', '200'], 话题: ['weather', 'calculation']

============================================================
[PASS] 所有测试通过！
```

## 注意事项

1. **会话隔离**：不同 conversation_id 的上下文完全隔离
2. **上下文长度**：默认保留最近20条消息，可配置
3. **意图权重**：不同意图有不同的权重配置
4. **实体缓存**：跨消息累积实体信息

## 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-18 | 初始版本 |
