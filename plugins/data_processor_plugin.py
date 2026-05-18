#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据处理工具插件"""

import math
from datetime import datetime, timedelta
from typing import List, Dict
from . import ToolPlugin

class DataProcessorPlugin(ToolPlugin):
    """数据处理工具插件类"""
    
    def __init__(self):
        super().__init__()
        
        # 单位换算配置
        self.conversion_factors = {
            # 长度
            'length': {
                'km_to_m': 1000, 'm_to_km': 0.001,
                'km_to_mile': 0.621371, 'mile_to_km': 1.60934,
                'm_to_ft': 3.28084, 'ft_to_m': 0.3048,
                'm_to_cm': 100, 'cm_to_m': 0.01,
                'cm_to_inch': 0.393701, 'inch_to_cm': 2.54,
                'm_to_yard': 1.09361, 'yard_to_m': 0.9144
            },
            # 重量
            'weight': {
                'kg_to_g': 1000, 'g_to_kg': 0.001,
                'kg_to_lb': 2.20462, 'lb_to_kg': 0.453592,
                'g_to_oz': 0.035274, 'oz_to_g': 28.3495,
                'ton_to_kg': 1000, 'kg_to_ton': 0.001
            },
            # 温度
            'temperature': {
                'c_to_f': lambda x: x * 9/5 + 32,
                'f_to_c': lambda x: (x - 32) * 5/9,
                'c_to_k': lambda x: x + 273.15,
                'k_to_c': lambda x: x - 273.15,
                'f_to_k': lambda x: (x - 32) * 5/9 + 273.15,
                'k_to_f': lambda x: (x - 273.15) * 9/5 + 32
            },
            # 面积
            'area': {
                'sqm_to_sqft': 10.7639, 'sqft_to_sqm': 0.092903,
                'sqkm_to_sqmile': 0.386102, 'sqmile_to_sqkm': 2.58999,
                'sqm_to_acre': 0.000247105, 'acre_to_sqm': 4046.86
            },
            # 体积
            'volume': {
                'l_to_ml': 1000, 'ml_to_l': 0.001,
                'l_to_gallon': 0.264172, 'gallon_to_l': 3.78541,
                'l_to_pint': 2.11338, 'pint_to_l': 0.473176
            },
            # 速度
            'speed': {
                'kmh_to_mph': 0.621371, 'mph_to_kmh': 1.60934,
                'ms_to_kmh': 3.6, 'kmh_to_ms': 0.277778
            }
        }
        
        # 单位名称映射
        self.unit_names = {
            'km': '千米', 'm': '米', 'cm': '厘米',
            'mile': '英里', 'ft': '英尺', 'inch': '英寸', 'yard': '码',
            'kg': '千克', 'g': '克', 'lb': '磅', 'oz': '盎司', 'ton': '吨',
            'c': '摄氏度', 'f': '华氏度', 'k': '开尔文',
            'sqm': '平方米', 'sqft': '平方英尺', 'sqkm': '平方千米', 'sqmile': '平方英里', 'acre': '英亩',
            'l': '升', 'ml': '毫升', 'gallon': '加仑', 'pint': '品脱',
            'kmh': '千米/小时', 'mph': '英里/小时', 'ms': '米/秒'
        }
    
    def get_name(self) -> str:
        """返回插件名称"""
        return "data"
    
    def get_description(self) -> str:
        """返回插件描述"""
        return "数据处理工具（单位换算、日期计算）"
    
    def get_usage(self) -> str:
        """返回使用说明"""
        return """
使用方法:
1. 单位换算: data convert --value <数值> --from <原单位> --to <目标单位>
2. 日期计算: data date --operation <操作> [--date <日期>] [--days <天数>]
3. 进制转换: data base --value <数值> --from <原进制> --to <目标进制>
4. 数学计算: data math --expression <表达式>

支持的单位类别:
- 长度: km, m, cm, mile, ft, inch, yard
- 重量: kg, g, lb, oz, ton
- 温度: c (摄氏度), f (华氏度), k (开尔文)
- 面积: sqm, sqft, sqkm, sqmile, acre
- 体积: l, ml, gallon, pint
- 速度: kmh, mph, ms

日期操作:
- add: 添加天数
- subtract: 减去天数
- diff: 计算两个日期差
- today: 获取今天日期
- weekday: 获取星期几

进制转换:
- 支持 2-36 进制

数学计算:
- 支持 +, -, *, /, **, sqrt, sin, cos, log 等

示例:
data convert --value 100 --from km --to mile
data date --operation add --date 2024-01-01 --days 7
data base --value 1010 --from 2 --to 10
data math --expression "sqrt(16) + sin(3.14)"
        """.strip()
    
    def get_parameters(self) -> List[str]:
        """返回参数列表"""
        return ["value", "from", "to", "operation", "date", "days", "expression"]
    
    def convert_unit(self, value: float, from_unit: str, to_unit: str) -> str:
        """单位换算"""
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        # 特殊处理温度
        if from_unit in ['c', 'f', 'k'] and to_unit in ['c', 'f', 'k']:
            return self._convert_temperature(value, from_unit, to_unit)
        
        # 查找转换因子
        for category, factors in self.conversion_factors.items():
            key = f"{from_unit}_to_{to_unit}"
            if key in factors:
                factor = factors[key]
                if callable(factor):
                    result = factor(value)
                else:
                    result = value * factor
                return f"{value} {self.unit_names.get(from_unit, from_unit)} = {result:.4f} {self.unit_names.get(to_unit, to_unit)}"
        
        return f"不支持从 {from_unit} 转换到 {to_unit}"
    
    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> str:
        """温度单位换算"""
        key = f"{from_unit}_to_{to_unit}"
        if key in self.conversion_factors['temperature']:
            converter = self.conversion_factors['temperature'][key]
            result = converter(value)
            return f"{value} {self.unit_names.get(from_unit, from_unit)} = {result:.2f} {self.unit_names.get(to_unit, to_unit)}"
        return "不支持的温度转换"
    
    def calculate_date(self, operation: str, date_str: str = None, days: int = 0) -> str:
        """日期计算"""
        operation = operation.lower()
        
        try:
            if operation == "today":
                today = datetime.now()
                return f"今天是 {today.strftime('%Y年%m月%d日')}，星期{self._get_weekday(today.weekday())}"
            
            elif operation == "weekday":
                if not date_str:
                    date = datetime.now()
                else:
                    date = self._parse_date(date_str)
                return f"{date.strftime('%Y年%m月%d日')} 是星期{self._get_weekday(date.weekday())}"
            
            elif operation == "add":
                if not date_str:
                    date = datetime.now()
                else:
                    date = self._parse_date(date_str)
                new_date = date + timedelta(days=days)
                return f"{date.strftime('%Y年%m月%d日')} + {days}天 = {new_date.strftime('%Y年%m月%d日')}，星期{self._get_weekday(new_date.weekday())}"
            
            elif operation == "subtract":
                if not date_str:
                    date = datetime.now()
                else:
                    date = self._parse_date(date_str)
                new_date = date - timedelta(days=days)
                return f"{date.strftime('%Y年%m月%d日')} - {days}天 = {new_date.strftime('%Y年%m月%d日')}，星期{self._get_weekday(new_date.weekday())}"
            
            elif operation == "diff":
                if not date_str:
                    return "请提供两个日期"
                dates = date_str.split(',')
                if len(dates) != 2:
                    return "请提供两个日期，用逗号分隔"
                date1 = self._parse_date(dates[0].strip())
                date2 = self._parse_date(dates[1].strip())
                diff = abs((date2 - date1).days)
                return f"{date1.strftime('%Y年%m月%d日')} 和 {date2.strftime('%Y年%m月%d日')} 相差 {diff} 天"
            
            else:
                return f"未知操作: {operation}"
        
        except Exception as e:
            return f"日期计算失败: {str(e)}"
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%Y年%m月%d日']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"无法解析日期: {date_str}")
    
    def _get_weekday(self, day: int) -> str:
        """获取星期名称"""
        weekdays = ['日', '一', '二', '三', '四', '五', '六']
        return weekdays[day]
    
    def convert_base(self, value: str, from_base: int, to_base: int) -> str:
        """进制转换"""
        try:
            # 转换为十进制
            decimal_value = int(value, from_base)
            
            # 转换为目标进制
            if to_base == 10:
                return f"{value} ({from_base}进制) = {decimal_value} (十进制)"
            elif to_base == 2:
                return f"{value} ({from_base}进制) = {bin(decimal_value)[2:]} (二进制)"
            elif to_base == 8:
                return f"{value} ({from_base}进制) = {oct(decimal_value)[2:]} (八进制)"
            elif to_base == 16:
                return f"{value} ({from_base}进制) = {hex(decimal_value)[2:].upper()} (十六进制)"
            else:
                # 通用进制转换
                digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                result = ""
                num = decimal_value
                while num > 0:
                    result = digits[num % to_base] + result
                    num = num // to_base
                return f"{value} ({from_base}进制) = {result} ({to_base}进制)"
        
        except Exception as e:
            return f"进制转换失败: {str(e)}"
    
    def calculate_math(self, expression: str) -> str:
        """数学计算"""
        try:
            # 安全的表达式计算
            # 只允许特定的数学函数和运算符
            allowed_funcs = {
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'log10': math.log10,
                'exp': math.exp,
                'abs': abs,
                'pow': pow,
                'pi': math.pi,
                'e': math.e
            }
            
            # 替换中文运算符
            expression = expression.replace('×', '*').replace('÷', '/')
            
            # 使用 eval 但限制可用函数
            result = eval(expression, {"__builtins__": {}}, allowed_funcs)
            
            return f"{expression} = {result}"
        
        except Exception as e:
            return f"计算失败: {str(e)}"
    
    def execute(self, *args, **kwargs) -> str:
        """执行工具调用"""
        if args:
            command = args[0]
            
            if command == "convert":
                value = float(kwargs.get("value", 0))
                from_unit = kwargs.get("from", "")
                to_unit = kwargs.get("to", "")
                return self.convert_unit(value, from_unit, to_unit)
            
            elif command == "date":
                operation = kwargs.get("operation", "")
                date_str = kwargs.get("date", "")
                days = int(kwargs.get("days", 0))
                return self.calculate_date(operation, date_str, days)
            
            elif command == "base":
                value = kwargs.get("value", "")
                from_base = int(kwargs.get("from", 10))
                to_base = int(kwargs.get("to", 10))
                return self.convert_base(value, from_base, to_base)
            
            elif command == "math":
                expression = kwargs.get("expression", "") or kwargs.get("expr", "")
                return self.calculate_math(expression)
            
            else:
                return f"未知命令: {command}"
        
        return self.get_usage()
