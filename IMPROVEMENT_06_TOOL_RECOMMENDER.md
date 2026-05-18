# 改进6：增强工具选择逻辑（智能工具推荐）

## 概述

为 AI Agent 系统添加了智能工具推荐模块，根据用户输入自动推荐最合适的工具。

## 功能特性

### 1. 关键词匹配
- 支持多关键词映射
- 支持权重配置
- 支持同义词识别

### 2. 置信度评估
- 计算工具匹配置信度
- 返回多个候选工具
- 提供决策解释

### 3. 工具优先级
- 当多个工具匹配时按优先级排序
- 可配置的优先级列表
- 支持动态调整

## 文件结构

```
tool_recommender.py    # 智能工具推荐模块
```

## 使用方法

### 基本使用

```python
from tool_recommender import tool_recommender, recommend_tool

# 推荐最佳工具
tool = recommend_tool("北京今天天气怎么样？")
print(tool)  # 输出: weather

# 获取详细推荐列表
results = tool_recommender.recommend_tools("帮我生成一张猫咪图片", top_n=3)
for r in results:
    print(f"{r['tool_name']}: {r['confidence']}%")

# 分析查询
analysis = tool_recommender.analyze_query("计算 1+2")

# 解释决策
explanation = tool_recommender.explain_decision("今天有什么新闻？")
print(explanation)
```

### 在 Agent 中集成

```python
from tool_recommender import recommend_tool

def process_message(user_input):
    # 智能推荐工具
    tool = recommend_tool(user_input)

    if tool:
        # 使用推荐的工具处理
        return call_tool(tool, user_input)
    else:
        # 直接由 LLM 处理
        return call_llm(user_input)
```

## 支持的工具

| 工具 | 关键词示例 | 权重 |
|------|----------|------|
| weather | 天气、温度、预报 | 2.0 |
| news | 新闻、头条、热点 | 1.5 |
| calculate | 计算、加减乘除 | 2.0 |
| file | 文件、读取、写入 | 1.5 |
| search | 搜索、查找 | 1.0 |
| get_current_time | 时间、几点 | 2.0 |
| image | 图片、生成、绘画 | 1.5 |
| memory | 记忆、回忆 | 1.0 |

## 测试结果

```
[INFO] 智能工具推荐器测试
============================================================
[TEST] 测试智能工具推荐器...
测试1: 天气查询 [PASS] - weather (16.67%)
测试2: 数学计算 [PASS] - calculate (36.36%)
测试3: 时间查询 [PASS] - get_current_time (57.14%)
测试4: 新闻查询 [PASS] - news (16.67%)
测试5: 图片生成 [PASS] - image (37.5%)
测试6: 获取最佳工具 [PASS] - weather
测试7: 分析查询 [PASS]
测试8: 决策解释 [PASS]

============================================================
[PASS] 所有测试通过！
```

## 注意事项

1. **关键词覆盖**：可根据实际需求添加更多关键词
2. **权重调整**：可根据使用频率调整工具权重
3. **优先级配置**：可根据业务场景调整工具优先级
4. **扩展性**：可轻松添加新的工具支持

## 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-18 | 初始版本 |
