#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间工具插件
"""

from datetime import datetime
from . import ToolPlugin

class TimePlugin(ToolPlugin):
    """时间工具插件"""
    
    def get_name(self) -> str:
        return "get_current_time"
    
    def get_description(self) -> str:
        return "获取当前时间"
    
    def get_usage(self) -> str:
        return "当用户询问时间、日期或星期几时调用此工具"
    
    def get_parameters(self) -> list:
        return []
    
    def execute(self) -> str:
        """获取当前时间"""
        now = datetime.now()
        weekday_map = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        weekday = weekday_map[now.weekday()]
        
        return f"当前时间：{now.strftime('%Y年%m月%d日')} {weekday} {now.strftime('%H:%M:%S')}"