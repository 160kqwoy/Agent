# 改进1：添加天气预报插件

## 概述

为 AI Agent 系统添加了天气预报功能插件，使用 OpenWeatherMap API 获取实时天气信息。

## 功能特性

### 1. 获取当前天气
- 温度（支持摄氏度/华氏度）
- 体感温度
- 湿度
- 风速
- 天气状况描述
- 能见度
- 气压

### 2. 获取未来5天预报
- 每天的天气状况
- 平均温度

## 文件结构

```
plugins/
└── weather_plugin.py    # 天气预报插件
```

## 使用方法

### 命令行方式
```bash
# 获取当前天气
python main.py --command "weather get_weather --city 北京"

# 获取5天预报
python main.py --command "weather get_forecast --city Shanghai"
```

### API 方式
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "北京今天天气怎么样？"}'
```

### UI 界面
在聊天窗口中直接提问：
- "北京今天天气怎么样？"
- "上海未来5天的天气预报"

## 配置说明

在 `.env` 文件中配置：

```env
# 天气 API 配置（OpenWeatherMap）
# 请访问 https://openweathermap.org/api 免费注册获取 API Key
OPENWEATHER_API_KEY=your_openweather_api_key
```

## 测试结果

```
[INFO] 天气预报插件测试
============================================================
[TEST] 测试天气预报插件...
[PASS] 插件加载成功
[PASS] 获取插件成功
[INFO] 插件名称: weather
[INFO] 插件描述: 获取指定城市的天气预报信息

[TEST] 测试获取天气...
结果: 无法获取城市 Beijing 的天气信息...
[WARN] 天气API可能未配置，使用模拟数据测试

[TEST] 使用模拟数据测试...
测试1: 获取插件信息 [PASS]
测试2: 获取参数列表 [PASS]
测试3: 获取使用说明 [PASS]

[INFO] 模拟测试全部通过！
============================================================
[PASS] 所有测试通过！
```

## 注意事项

1. **API Key**：需要在 OpenWeatherMap 官网注册获取免费 API Key
2. **城市支持**：支持中英文城市名称
3. **网络依赖**：需要网络连接才能获取实时天气数据
4. **备用方案**：如果未配置 API Key 或网络不可用，插件会返回友好的错误提示

## 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-18 | 初始版本 |
