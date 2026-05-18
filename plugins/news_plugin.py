#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""新闻资讯插件 - 使用 NewsAPI 获取最新新闻"""

import os
import requests
from typing import List
from . import ToolPlugin

class NewsPlugin(ToolPlugin):
    """新闻资讯插件类"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get("NEWSAPI_KEY", "demo_key")
        self.base_url = "https://newsapi.org/v2"
    
    def get_name(self) -> str:
        """返回插件名称"""
        return "news"
    
    def get_description(self) -> str:
        """返回插件描述"""
        return "获取最新新闻资讯"
    
    def get_usage(self) -> str:
        """返回使用说明"""
        return """
使用方法:
1. 获取头条新闻: news get_top_headlines [--country <国家代码>] [--category <分类>]
2. 搜索新闻: news search --q <关键词> [--language <语言代码>]

支持的国家代码: cn, us, jp, gb, de 等
支持的分类: business, entertainment, general, health, science, sports, technology
支持的语言: zh, en, ja, fr 等

示例:
news get_top_headlines --country cn
news get_top_headlines --country us --category technology
news search --q AI --language zh
        """.strip()
    
    def get_parameters(self) -> List[str]:
        """返回参数列表"""
        return ["country", "category", "q", "language"]
    
    def get_top_headlines(self, country: str = "cn", category: str = "") -> str:
        """获取头条新闻"""
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                "apiKey": self.api_key,
                "country": country,
                "language": "zh" if country == "cn" else "en"
            }
            
            if category:
                params["category"] = category
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                
                if not articles:
                    return f"暂无{country}的头条新闻"
                
                result = f"📰 {country.upper()} 头条新闻\n\n"
                for i, article in enumerate(articles[:5], 1):
                    title = article.get("title", "")
                    source = article.get("source", {}).get("name", "")
                    url = article.get("url", "")
                    result += f"{i}. {title}\n   来源: {source}\n   链接: {url}\n\n"
                
                return result.strip()
            else:
                return f"获取新闻失败: {response.status_code}"
        except Exception as e:
            return f"获取新闻异常: {str(e)}"
    
    def search_news(self, query: str, language: str = "zh") -> str:
        """搜索新闻"""
        try:
            url = f"{self.base_url}/everything"
            params = {
                "apiKey": self.api_key,
                "q": query,
                "language": language,
                "sortBy": "publishedAt"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                
                if not articles:
                    return f"未找到关于 '{query}' 的新闻"
                
                result = f"🔍 关于 '{query}' 的新闻\n\n"
                for i, article in enumerate(articles[:5], 1):
                    title = article.get("title", "")
                    source = article.get("source", {}).get("name", "")
                    url = article.get("url", "")
                    result += f"{i}. {title}\n   来源: {source}\n   链接: {url}\n\n"
                
                return result.strip()
            else:
                return f"搜索新闻失败: {response.status_code}"
        except Exception as e:
            return f"搜索新闻异常: {str(e)}"
    
    def execute(self, *args, **kwargs) -> str:
        """执行工具调用"""
        if args:
            command = args[0]
            if command == "get_top_headlines":
                country = kwargs.get("country", "cn") or (args[1] if len(args) > 1 else "cn")
                category = kwargs.get("category", "") or (args[2] if len(args) > 2 else "")
                return self.get_top_headlines(country, category)
            elif command == "search":
                query = kwargs.get("q", "") or kwargs.get("query", "") or (args[1] if len(args) > 1 else "")
                language = kwargs.get("language", "zh")
                return self.search_news(query, language)
            else:
                return f"未知命令: {command}"
        return "请提供命令参数"
