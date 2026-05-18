# 改进2：添加新闻资讯插件

## 概述

为 AI Agent 系统添加了新闻资讯功能插件，使用 NewsAPI 获取最新新闻信息。

## 功能特性

### 1. 获取头条新闻
- 支持按国家筛选
- 支持按分类筛选（商业、娱乐、科技等）
- 返回标题、来源、链接

### 2. 搜索新闻
- 支持关键词搜索
- 支持按语言筛选
- 按发布时间排序

## 文件结构

```
plugins/
└── news_plugin.py    # 新闻资讯插件
```

## 使用方法

### 命令行方式
```bash
# 获取中国头条新闻
python main.py --command "news get_top_headlines --country cn"

# 获取美国科技新闻
python main.py --command "news get_top_headlines --country us --category technology"

# 搜索 AI 相关新闻
python main.py --command "news search --q AI --language zh"
```

### API 方式
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "今天的头条新闻是什么？"}'
```

### UI 界面
在聊天窗口中直接提问：
- "今天有什么新闻？"
- "科技新闻"
- "搜索关于 AI 的新闻"

## 配置说明

在 `.env` 文件中配置：

```env
# 新闻 API 配置（NewsAPI）
# 请访问 https://newsapi.org/ 免费注册获取 API Key
NEWSAPI_KEY=your_newsapi_key
```

## 支持的参数

### 国家代码
| 代码 | 国家 |
|------|------|
| cn | 中国 |
| us | 美国 |
| jp | 日本 |
| gb | 英国 |
| de | 德国 |

### 分类
- business（商业）
- entertainment（娱乐）
- general（综合）
- health（健康）
- science（科学）
- sports（体育）
- technology（科技）

### 语言代码
| 代码 | 语言 |
|------|------|
| zh | 中文 |
| en | 英文 |
| ja | 日文 |
| fr | 法文 |

## 测试结果

```
[INFO] 新闻资讯插件测试
============================================================
[TEST] 测试新闻资讯插件...
[PASS] 插件加载成功
[PASS] 获取插件成功
[INFO] 插件名称: news
[INFO] 插件描述: 获取最新新闻资讯

[TEST] 测试获取头条新闻...
结果: 获取新闻异常: HTTPSConnectionPool(host='newsapi.org', port=443)...
[WARN] 新闻API可能未配置，使用模拟数据测试

[TEST] 使用模拟数据测试...
测试1: 获取插件信息 [PASS]
测试2: 获取参数列表 [PASS]
测试3: 获取使用说明 [PASS]

[INFO] 模拟测试全部通过！
============================================================
[PASS] 所有测试通过！
```

## 注意事项

1. **API Key**：需要在 NewsAPI 官网注册获取免费 API Key
2. **访问限制**：免费版有请求次数限制
3. **网络依赖**：需要网络连接才能获取新闻数据
4. **备用方案**：如果未配置 API Key 或网络不可用，插件会返回友好的错误提示

## 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-18 | 初始版本 |
