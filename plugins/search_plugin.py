#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络搜索工具插件
"""

import requests
from . import ToolPlugin

class SearchPlugin(ToolPlugin):
    """网络搜索工具插件"""
    
    def get_name(self) -> str:
        return "web_search"
    
    def get_description(self) -> str:
        return "进行网络搜索"
    
    def get_usage(self) -> str:
        return "当用户询问新闻、天气、时事、百科知识或需要实时信息时调用此工具，参数为搜索关键词"
    
    def get_parameters(self) -> list:
        return ["query"]
    
    def execute(self, query: str) -> str:
        """执行网络搜索"""
        try:
            # 使用 DuckDuckGo API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 构建结果
            results = []
            
            # 添加快速回答
            if "Abstract" in data and data["Abstract"]:
                results.append(f"📌 快速回答: {data['Abstract']}")
            
            # 添加搜索结果
            if "Results" in data and data["Results"]:
                results.append("\n🔍 搜索结果:")
                for i, result in enumerate(data["Results"][:3], 1):
                    title = result.get("Text", "无标题")
                    url = result.get("FirstURL", "")
                    results.append(f"{i}. {title}")
                    if url:
                        results.append(f"   {url}")
            
            # 如果没有结果
            if not results:
                return f"未找到关于 '{query}' 的搜索结果"
            
            return "\n".join(results)
        
        except requests.exceptions.RequestException as e:
            return f"搜索失败: {str(e)}"
        except Exception as e:
            return f"搜索异常: {str(e)}"