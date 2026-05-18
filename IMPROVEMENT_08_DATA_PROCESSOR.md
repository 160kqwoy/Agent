# 改进8：数据处理工具插件

## 概述

为 AI Agent 系统添加了数据处理工具插件，支持单位换算、日期计算、进制转换和数学计算功能。

## 功能特性

### 1. 单位换算
- **长度**：千米、米、厘米、英里、英尺、英寸、码
- **重量**：千克、克、磅、盎司、吨
- **温度**：摄氏度、华氏度、开尔文
- **面积**：平方米、平方英尺、平方千米、平方英里、英亩
- **体积**：升、毫升、加仑、品脱
- **速度**：千米/小时、英里/小时、米/秒

### 2. 日期计算
- 获取今天日期
- 添加/减去天数
- 计算两个日期差
- 获取星期几

### 3. 进制转换
- 支持 2-36 进制转换
- 二进制、八进制、十进制、十六进制

### 4. 数学计算
- 支持基本运算符：+、-、*、/、**
- 支持数学函数：sqrt、sin、cos、tan、log、exp

## 文件结构

```
plugins/
└── data_processor_plugin.py    # 数据处理插件
```

## 使用方法

### 命令行方式
```bash
# 单位换算
python main.py --command "data convert --value 100 --from km --to mile"

# 日期计算
python main.py --command "data date --operation add --date 2024-01-01 --days 7"

# 进制转换
python main.py --command "data base --value 1010 --from 2 --to 10"

# 数学计算
python main.py --command "data math --expression sqrt(16) + 3"
```

### API 方式
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "100公里等于多少英里？"}'
```

### 代码调用
```python
from plugins import plugin_manager

plugin_manager.load_plugin("data_processor_plugin")
data_plugin = plugin_manager.get_plugin("data")

# 单位换算
result = data_plugin.convert_unit(100, "km", "mile")

# 日期计算
result = data_plugin.calculate_date("add", "2024-01-01", 7)

# 进制转换
result = data_plugin.convert_base("1010", 2, 10)

# 数学计算
result = data_plugin.calculate_math("sqrt(16) + 3")
```

## 测试结果

```
[INFO] 数据处理工具插件测试
============================================================
[TEST] 测试数据处理工具插件...
[PASS] 插件加载成功
[PASS] 获取插件成功

测试1: 长度单位换算 [PASS] - 100 千米 = 62.1371 英里
测试2: 温度换算 [PASS] - 25 摄氏度 = 77.00 华氏度
测试3: 获取今天日期 [PASS] - 今天是 2026年05月18日，星期日
测试4: 添加天数 [PASS] - 2024年01月01日 + 7天 = 2024年01月08日
测试5: 进制转换 [PASS] - 1010 (2进制) = 10 (十进制)
测试6: 数学计算 [PASS] - sqrt(16) + 3 = 7.0
测试7: 命令执行 [PASS] - 100.0 千克 = 220.4620 磅

============================================================
[PASS] 所有测试通过！
```

## 注意事项

1. **温度转换**：摄氏度、华氏度、开尔文之间可以互相转换
2. **日期格式**：支持 YYYY-MM-DD、YYYY/MM/DD、YYYY.MM.DD 格式
3. **进制范围**：支持 2-36 进制转换
4. **数学计算**：支持基本数学函数，使用 eval 执行

## 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-18 | 初始版本 |
