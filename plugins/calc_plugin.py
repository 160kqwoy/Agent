#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算器工具插件
"""

import math
import re
from . import ToolPlugin

class CalculatorPlugin(ToolPlugin):
    """计算器工具插件"""
    
    def get_name(self) -> str:
        return "calculate"
    
    def get_description(self) -> str:
        return "执行数学运算"
    
    def get_usage(self) -> str:
        return "当用户需要进行数学计算时调用此工具，参数为数学表达式"
    
    def get_parameters(self) -> list:
        return ["expression"]
    
    def execute(self, expression: str) -> str:
        """执行数学计算"""
        try:
            # 清理表达式
            expression = expression.strip()
            
            # 支持的运算符和函数
            allowed_pattern = r"^[0-9+\-*/().\s]+$"
            
            # 安全检查
            if not re.match(allowed_pattern, expression):
                return f"错误：不支持的表达式格式"
            
            # 执行计算
            result = eval(expression)
            
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            
            return f"计算结果：{expression} = {result}"
        
        except ZeroDivisionError:
            return "错误：不能除以零"
        except Exception as e:
            return f"计算失败: {str(e)}"