# 改进3：增强记忆机制（添加长期记忆存储）

## 概述

为 AI Agent 系统添加了长期记忆管理模块，支持用户对话历史的持久化存储和检索。

## 功能特性

### 1. 记忆存储
- 使用 JSON 文件持久化存储
- 支持自定义元数据
- 自动保存和加载

### 2. 记忆检索
- 关键词搜索
- 相似度匹配
- 最近记忆获取

### 3. 记忆管理
- 添加、删除、清空记忆
- 访问时间追踪
- 统计信息查询

## 文件结构

```
memory_manager.py    # 记忆管理器模块
memory.json          # 记忆数据文件（自动生成）
```

## 使用方法

### 基本使用

```python
from memory_manager import memory_manager, add_memory, search_memories

# 添加记忆
add_memory("用户喜欢人工智能", {"user": "user1", "type": "preference"})

# 搜索记忆
results = search_memories("人工智能")
for mem in results:
    print(mem.content)

# 获取最近记忆
recent = memory_manager.get_recent_memories(10)

# 获取统计信息
stats = memory_manager.get_statistics()
```

### 在 Agent 中集成

```python
from memory_manager import memory_manager

# 在对话结束时保存记忆
def save_conversation_memory(user_input, response):
    memory_manager.add_memory(
        f"用户问: {user_input}\nAI回答: {response}",
        {"type": "conversation", "timestamp": datetime.now().isoformat()}
    )

# 在回答前搜索相关记忆
def get_relevant_memories(query):
    return memory_manager.search_memories(query, limit=5)
```

## API 说明

| 方法 | 说明 | 参数 |
|------|------|------|
| `add_memory(content, metadata)` | 添加记忆 | content: 记忆内容, metadata: 元数据(可选) |
| `get_memory(memory_id)` | 获取单个记忆 | memory_id: 记忆ID |
| `search_memories(query, limit, threshold)` | 搜索记忆 | query: 搜索词, limit: 数量限制, threshold: 相似度阈值 |
| `get_recent_memories(limit)` | 获取最近记忆 | limit: 数量限制 |
| `delete_memory(memory_id)` | 删除记忆 | memory_id: 记忆ID |
| `clear_all_memories()` | 清空所有记忆 | 无 |
| `get_memory_count()` | 获取记忆数量 | 无 |
| `get_statistics()` | 获取统计信息 | 无 |

## 测试结果

```
[INFO] 记忆管理器测试
============================================================
[TEST] 测试记忆管理器...
测试1: 添加记忆 [PASS]
测试2: 获取记忆 [PASS]
测试3: 添加多条记忆 [PASS]
测试4: 搜索记忆 [PASS]，找到 1 条相关记忆
测试5: 获取最近记忆 [PASS]，获取到 4 条记忆
测试6: 获取统计信息 [PASS]，总记忆数: 4
测试7: 删除记忆 [PASS]

============================================================
[PASS] 所有测试通过！
```

## 注意事项

1. **数据持久化**：记忆自动保存到 `memory.json` 文件
2. **搜索算法**：基于字符相似度的简单匹配算法
3. **扩展性**：可扩展为使用向量数据库进行语义搜索
4. **性能**：适合中小规模记忆存储，大规模场景建议使用数据库

## 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-18 | 初始版本，使用 JSON 文件存储 |
