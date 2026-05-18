# 改进7：文本处理工具插件

## 概述

为 AI Agent 系统添加了文本处理工具插件，支持文本摘要、关键词提取、格式转换和拼音转换功能。

## 功能特性

### 1. 文本摘要
- 自动提取文本核心内容
- 支持自定义摘要长度
- 基于词频和位置权重的算法

### 2. 关键词提取
- 统计词频提取关键词
- 支持自定义返回数量

### 3. 格式转换
- Markdown → 纯文本
- HTML → 纯文本
- 纯文本 → Markdown

### 4. 拼音转换
- 中文转拼音
- 支持常用汉字

## 文件结构

```
plugins/
└── text_processor_plugin.py    # 文本处理插件
```

## 使用方法

### 命令行方式
```bash
# 文本摘要
python main.py --command "text summarize --text 人工智能是计算机科学的一个分支..."

# 关键词提取
python main.py --command "text keywords --text 人工智能技术发展迅速 --count 5"

# 格式转换
python main.py --command "text convert --text '# 标题' --from markdown --to plain"

# 拼音转换
python main.py --command "text pinyin --text 你好世界"
```

### API 方式
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "帮我总结这段文字：人工智能是计算机科学的一个分支..."}'
```

### 代码调用
```python
from plugins import plugin_manager

plugin_manager.load_plugin("text_processor_plugin")
text_plugin = plugin_manager.get_plugin("text")

# 文本摘要
summary = text_plugin.summarize("长文本内容", max_length=100)

# 关键词提取
keywords = text_plugin.extract_keywords("文本内容", top_n=5)

# 格式转换
plain_text = text_plugin.convert_format("# 标题", "markdown", "plain")

# 拼音转换
pinyin = text_plugin.to_pinyin("你好世界")
```

## 测试结果

```
[INFO] 文本处理工具插件测试
============================================================
[TEST] 测试文本处理工具插件...
[PASS] 插件加载成功
[PASS] 获取插件成功

测试1: 文本摘要 [PASS]
测试2: 关键词提取 [PASS]
测试3: Markdown转纯文本 [PASS]
测试4: HTML转纯文本 [PASS]
测试5: 拼音转换 [PASS]
测试6: 执行命令 [PASS]

============================================================
[PASS] 所有测试通过！
```

## 注意事项

1. **文本摘要**：基于简单的词频算法，对于复杂文本可能效果有限
2. **关键词提取**：目前按空格分词，对于中文连续文本效果一般
3. **拼音转换**：使用简单映射表，支持常用汉字

## 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-18 | 初始版本 |
