# 改进4：容器化部署（Docker）

## 概述

为 AI Agent 系统添加了 Docker 容器化支持，便于快速部署和运行。

## 功能特性

### 1. Docker 镜像构建
- 使用 Python 3.10 基础镜像
- 自动安装所有依赖
- 支持 Streamlit UI 和 FastAPI

### 2. Docker Compose 部署
- 支持多容器部署
- 环境变量配置
- 数据卷持久化

## 文件结构

```
Dockerfile           # Docker 镜像构建配置
docker-compose.yml   # Docker Compose 部署配置
.dockerignore        # Docker 构建忽略文件
```

## 使用方法

### 方法1：使用 Docker CLI

```bash
# 构建镜像
docker build -t ai-agent .

# 运行容器
docker run -p 8501:8501 -e LLM_API_KEY=your_key ai-agent

# 完整配置运行
docker run -p 8501:8501 -p 8000:8000 \
  -e LLM_API_KEY=your_key \
  -e LLM_BASE_URL=http://localhost:8000/v1 \
  -e LLM_MODEL=Qwen3.5-14B \
  -v $(pwd)/memory.json:/app/memory.json \
  -v $(pwd)/logs:/app/logs \
  ai-agent
```

### 方法2：使用 Docker Compose

```bash
# 创建 .env 文件
cp .env.example .env

# 编辑 .env 文件配置环境变量

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方法3：启动 API 服务

```bash
# 只启动 API 服务
docker-compose up -d api

# 或使用 Docker
docker run -p 8000:8000 \
  -e LLM_API_KEY=your_key \
  ai-agent uvicorn api_server:app --host 0.0.0.0 --port 8000
```

## 环境变量配置

在 `.env` 文件中配置：

```env
# LLM 配置
LLM_API_KEY=your_api_key
LLM_BASE_URL=http://localhost:8000/v1
LLM_MODEL=Qwen3.5-14B

# 天气 API
OPENWEATHER_API_KEY=your_openweather_api_key

# 新闻 API
NEWSAPI_KEY=your_newsapi_key
```

## 端口说明

| 端口 | 服务 | 说明 |
|------|------|------|
| 8501 | Streamlit UI | 图形化界面 |
| 8000 | FastAPI | RESTful API |

## 数据持久化

```
├── memory.json       # 记忆数据（挂载）
├── chat_history.json # 聊天历史（挂载）
└── logs/            # 日志目录（挂载）
```

## 测试结果

```
[INFO] Docker 配置测试
============================================================
[TEST] 测试 Docker 配置...
测试1: 检查 Dockerfile [PASS]
测试2: 检查 docker-compose.yml [PASS]
测试3: 检查 .dockerignore [PASS]
测试4: 检查 Dockerfile 内容 [PASS]
测试5: 检查 docker-compose.yml 内容 [PASS]
测试6: 检查 requirements.txt [PASS]

============================================================
[PASS] 所有测试通过！

部署说明:
1. 构建镜像: docker build -t ai-agent .
2. 运行容器: docker run -p 8501:8501 ai-agent
3. 或使用 compose: docker-compose up -d
```

## 注意事项

1. **Docker 环境**：需要安装 Docker 和 Docker Compose
2. **环境变量**：运行前需要配置必要的环境变量
3. **数据卷**：建议挂载记忆和日志目录以持久化数据
4. **网络配置**：确保 LLM 服务地址可以从容器内部访问

## 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-18 | 初始版本 |
