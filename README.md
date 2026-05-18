# AI Agent 系统

基于 LangChain 和本地 LLM 的智能代理系统。

## 功能特性

- 🤖 **本地 LLM 支持**：支持连接本地运行的大语言模型（如 Qwen3.5）
- 🧮 **计算器工具**：执行数学运算（加减乘除、三角函数、对数等）
- ⏰ **时间查询**：获取当前时间和日期
- 📄 **文件读取**：读取本地文本文件内容
- ✏️ **文件写入**：创建或修改文本文件
- 🗑️ **文件删除**：删除本地文件
- 💬 **对话记忆**：记住历史对话，支持上下文理解
- 🔄 **ReAct 循环**：实现思考-行动-观察的推理循环
- 🌤️ **天气预报**：获取实时天气和未来预报
- 📰 **新闻资讯**：获取最新头条新闻
- 🖼️ **图片生成**：使用 DALL-E 生成图片
- 📝 **文本处理**：文本摘要、关键词提取、格式转换、拼音转换
- 🔢 **数据处理**：单位换算、日期计算、进制转换
- 🎯 **智能工具推荐**：自动推荐最合适的工具
- 💾 **长期记忆**：持久化存储记忆
- 📊 **性能优化**：缓存、限流、异步处理
- 🧠 **对话上下文增强**：意图识别、实体提取、指代解析

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置环境变量

在 `.env` 文件中配置以下参数：

```env
LLM_BASE_URL=http://127.0.0.1:1234/v1
LLM_MODEL=Qwen3.5 9B
LLM_API_KEY=sk-placeholder

# 可选 API 配置
OPENWEATHER_API_KEY=your_openweather_api_key
NEWSAPI_KEY=your_newsapi_key
OPENAI_API_KEY=your_openai_api_key
```

## 使用方法

### 命令行模式

```bash
python main.py
```

然后在终端中输入问题与 Agent 交互：

```
请输入您的问题: 今天星期几
Agent 回答: 今天是星期三哦～

请输入您的问题: 计算 23 * 45 + 100
Agent 回答: 23 × 45 + 100 等于 1135 哦～

请输入您的问题: 读取 requirements.txt
Agent 回答: 文件内容如下...

请输入您的问题: exit
感谢使用 AI Agent，再见！
```

### 图形化界面模式

```bash
streamlit run ui_app.py
```

界面功能：
- 聊天窗口：显示对话历史和消息输入
- 控制面板：初始化、保存/清空历史
- 工具列表：显示所有可用工具及其描述
- 性能监控：显示 API 调用统计和响应时间
- 深色模式切换
- 聊天历史导出（JSON/Markdown/TXT）
- 消息复制功能

### API 服务模式

```bash
python api_server.py
```

服务将在 http://localhost:8000 启动

## 支持的工具

| 工具名称 | 功能描述 | 触发关键词 |
|---------|---------|-----------|
| calculate | 执行数学运算 | 计算、加、减、乘、除、等于、+、-、*、/ |
| get_current_time | 获取当前时间 | 时间、日期、星期、今天 |
| file | 文件读取/写入/删除 | 读取、查看、内容、新建、写入、删除 |
| weather | 获取天气预报 | 天气、温度、预报 |
| news | 获取新闻资讯 | 新闻、头条、热点 |
| image | AI 图片生成 | 图片、生成、照片 |
| text | 文本处理 | 摘要、关键词、格式、拼音 |
| data | 数据处理 | 换算、转换、进制、计算 |
| memory | 长期记忆存储 | 记忆、回忆 |

## 更新说明

### v1.0.0 (2026-04-22)
- ✅ 初始版本发布
- ✅ 集成计算器工具
- ✅ 集成时间查询工具
- ✅ 支持对话记忆功能
- ✅ 使用 ReAct 循环模式
- ✅ 支持本地 LLM 连接

### v1.1.0 (2026-04-22)
- ✅ 添加文件读取工具（FileReader）
- ✅ 修复星期计算错误
- ✅ 优化工具调用逻辑
- ✅ 增加安全检查（防止路径遍历攻击）

### v1.2.0 (2026-04-22)
- ✅ 添加文件写入工具（FileWriter）
- ✅ 添加文件删除工具（FileDeleter）
- ✅ 更新 README.md 文档
- ✅ 增强文件操作安全性

### v1.3.0 (2026-05-06)
- ✅ 重构工具选择机制
- ✅ 实现基于 LLM 的智能工具选择
- ✅ 引入工具注册表（TOOLS）
- ✅ 支持多格式工具调用解析
- ✅ 实现完整的 ReAct 循环

### v1.4.0 (2026-05-06)
- ✅ 实现多轮推理支持
- ✅ 支持复杂任务的多步骤分解
- ✅ 添加中间步骤可视化显示
- ✅ 实现反思机制
- ✅ 支持完成标记【完成】

### v1.5.0 (2026-05-06)
- ✅ 实现对话历史持久化
- ✅ 自动保存对话历史到 JSON 文件
- ✅ 程序启动时自动加载历史记录

### v1.6.0 (2026-05-06)
- ✅ 实现日志系统
- ✅ 支持控制台和文件双输出
- ✅ 支持日志级别配置

### v1.7.0 (2026-05-06)
- ✅ 实现配置管理系统
- ✅ 支持 JSON 配置文件
- ✅ 支持环境变量覆盖配置

### v1.8.0 (2026-05-06)
- ✅ 添加网络搜索工具
- ✅ 支持中英文搜索

### v1.9.0 (2026-05-06)
- ✅ 实现安全输入过滤系统
- ✅ 检测 SQL 注入、命令注入等攻击

### v1.10.0 (2026-05-06)
- ✅ 实现 RESTful API 接口
- ✅ 提供聊天、历史管理接口

### v1.11.0 (2026-05-06)
- ✅ 实现插件化架构
- ✅ 动态加载工具插件
- ✅ 支持插件热更新

### v1.12.0 (2026-05-06)
- ✅ 实现错误恢复机制
- ✅ 自动重试 + 故障转移

### v1.13.0 (2026-05-06)
- ✅ 实现性能监控系统

### v1.14.0 (2026-05-06)
- ✅ 实现图形化界面（Streamlit）

### v2.0.0 (2026-05-18) - 插件扩展版本

#### 改进1：添加天气预报插件
- ✅ 获取当前天气（温度、湿度、风速等）
- ✅ 获取未来5天预报
- ✅ 支持中英文城市名称
- 文件：`plugins/weather_plugin.py`

#### 改进2：添加新闻资讯插件
- ✅ 获取头条新闻（按国家/分类筛选）
- ✅ 关键词搜索新闻
- ✅ 支持多语言
- 文件：`plugins/news_plugin.py`

#### 改进3：增强记忆机制
- ✅ JSON 文件持久化存储
- ✅ 关键词搜索和相似度匹配
- ✅ 访问时间追踪
- 文件：`memory_manager.py`

#### 改进4：容器化部署
- ✅ Dockerfile 镜像构建
- ✅ Docker Compose 多容器部署
- ✅ 数据卷持久化
- 文件：`Dockerfile`, `docker-compose.yml`

#### 改进5：添加图片生成功能
- ✅ DALL-E API 集成
- ✅ 支持多种尺寸选择
- 文件：`plugins/image_plugin.py`

#### 改进6：智能工具推荐
- ✅ 关键词匹配 + 置信度评估
- ✅ 工具优先级排序
- ✅ 决策解释
- 文件：`tool_recommender.py`

#### 改进7：文本处理工具插件
- ✅ 文本摘要（基于词频算法）
- ✅ 关键词提取
- ✅ 格式转换（Markdown/HTML/纯文本）
- ✅ 拼音转换
- 文件：`plugins/text_processor_plugin.py`

#### 改进8：数据处理工具插件
- ✅ 单位换算（长度、重量、温度、面积、体积、速度）
- ✅ 日期计算（加减天数、日期差、星期几）
- ✅ 进制转换（2-36进制）
- ✅ 数学计算（基本运算和函数）
- 文件：`plugins/data_processor_plugin.py`

#### 改进9：UI交互优化
- ✅ 聊天历史导出（JSON/Markdown/TXT）
- ✅ 深色/浅色主题切换
- ✅ 消息复制按钮
- ✅ 时间戳支持
- 文件：`ui_app.py`

#### 改进10：对话上下文增强
- ✅ 多会话上下文管理
- ✅ 意图识别（9种意图类型）
- ✅ 实体提取（地点、日期、数字、话题）
- ✅ 指代解析
- ✅ 话题跟踪和变化检测
- 文件：`context_manager.py`

#### 改进11：性能优化
- ✅ LRU 缓存管理器（支持 TTL 过期）
- ✅ 请求限流器（滑动窗口）
- ✅ 异步任务管理器
- ✅ 性能计时器
- 文件：`performance_optimizer.py`

## 项目结构

```
.
├── main.py                      # 主程序文件
├── ui_app.py                    # Streamlit 图形界面
├── api_server.py                # FastAPI 服务
├── requirements.txt             # 依赖列表
├── .env                         # 环境变量配置
├── Dockerfile                   # Docker 镜像配置
├── docker-compose.yml           # Docker Compose 配置
├── README.md                    # 项目说明文档
│
├── plugins/                     # 插件目录
│   ├── __init__.py
│   ├── weather_plugin.py        # 天气预报插件
│   ├── news_plugin.py           # 新闻资讯插件
│   ├── image_plugin.py          # 图片生成插件
│   ├── text_processor_plugin.py # 文本处理插件
│   └── data_processor_plugin.py # 数据处理插件
│
├── memory_manager.py            # 记忆管理器
├── tool_recommender.py          # 智能工具推荐
├── context_manager.py           # 对话上下文管理
├── performance_optimizer.py     # 性能优化
│
└── test_*.py                    # 测试文件
```

## API 接口

### 接口列表

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /health | 健康检查 |
| POST | /chat | 发送消息 |
| GET | /tools | 获取可用工具列表 |
| GET | /history/summary | 获取对话历史摘要 |
| POST | /history/save | 保存对话历史 |
| DELETE | /history | 清空对话历史 |

### 使用示例

```bash
# 发送消息
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "session_id": "abc123"}'

# 响应
{
  "response": "您好！有什么可以帮助您的？",
  "session_id": "abc123",
  "tool_used": false,
  "tool_info": null
}
```

## Docker 部署

### 使用 Docker CLI

```bash
# 构建镜像
docker build -t ai-agent .

# 运行容器
docker run -p 8501:8501 -e LLM_API_KEY=your_key ai-agent
```

### 使用 Docker Compose

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 注意事项

1. 确保本地 LLM 服务已启动并运行在配置的端口上
2. 文件读取工具只支持当前目录下的文件，不支持路径遍历
3. 建议将敏感数据（如 API Key）存储在 `.env` 文件中，不要提交到版本控制
4. 部分功能需要配置相应的 API Key（天气、新闻、图片生成）

## 许可证

MIT License
