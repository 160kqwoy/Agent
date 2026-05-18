#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""智能工具推荐模块"""

from typing import List, Dict, Tuple, Optional
import re

class ToolRecommender:
    """智能工具推荐器"""
    
    def __init__(self):
        # 工具关键词映射（关键词越多权重越高）
        self.tool_keywords = {
            "weather": {
                "keywords": ["天气", "温度", "预报", "下雨", "晴天", "多云", "气温", "气候", "台风", "刮风", "下雪", "雾霾"],
                "description": "获取天气信息",
                "weight": 2.0  # 权重
            },
            "news": {
                "keywords": ["新闻", "资讯", "头条", "报道", "最新", "热点", "事件", "新闻联播", "发布会"],
                "description": "获取新闻资讯",
                "weight": 1.5
            },
            "calculate": {
                "keywords": ["计算", "加", "减", "乘", "除", "等于", "多少", "求和", "结果", "公式", "运算"],
                "description": "执行数学计算",
                "weight": 2.0
            },
            "file": {
                "keywords": ["文件", "读取", "写入", "保存", "创建", "删除", "txt", "文档"],
                "description": "文件操作",
                "weight": 1.5
            },
            "search": {
                "keywords": ["搜索", "查找", "查询", "百度", "google", "bing"],
                "description": "网络搜索",
                "weight": 1.0
            },
            "get_current_time": {
                "keywords": ["时间", "几点", "现在", "日期", "星期", "几点钟", "时刻"],
                "description": "获取当前时间",
                "weight": 2.0
            },
            "image": {
                "keywords": ["图片", "生成", "照片", "画图", "图像", "设计", "创作", "绘画"],
                "description": "生成图片",
                "weight": 1.5
            },
            "memory": {
                "keywords": ["记忆", "记住", "回忆", "之前", "历史", "记录"],
                "description": "长期记忆",
                "weight": 1.0
            }
        }
        
        # 工具优先级（当多个工具匹配度相同时的优先级）
        self.tool_priority = [
            "calculate",      # 计算优先
            "get_current_time", # 时间优先
            "weather",        # 天气次之
            "news",           # 新闻
            "image",          # 图片生成
            "file",           # 文件操作
            "memory",         # 记忆
            "search"          # 搜索兜底
        ]
    
    def analyze_query(self, query: str) -> List[Tuple[str, float]]:
        """分析查询并返回工具匹配度"""
        results = []
        
        for tool_name, config in self.tool_keywords.items():
            score = self._calculate_match_score(query, config["keywords"]) * config.get("weight", 1.0)
            if score > 0:
                results.append((tool_name, score, config["description"]))
        
        # 按分数排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def _calculate_match_score(self, query: str, keywords: List[str]) -> float:
        """计算匹配分数"""
        score = 0.0
        query_lower = query.lower()
        
        for keyword in keywords:
            if keyword in query_lower:
                # 根据关键词在查询中的重要性调整分数
                if len(keyword) >= 2:
                    score += 1.0
                else:
                    score += 0.5
        
        # 归一化到 0-100
        return (score / len(keywords)) * 100 if keywords else 0.0
    
    def recommend_tools(self, query: str, top_n: int = 3) -> List[Dict[str, any]]:
        """推荐工具"""
        matches = self.analyze_query(query)
        
        # 按优先级排序（分数相同时优先级高的排前面）
        matches.sort(key=lambda x: (x[1], -self.tool_priority.index(x[0]) if x[0] in self.tool_priority else 999), reverse=True)
        
        results = []
        for tool_name, score, description in matches[:top_n]:
            results.append({
                "tool_name": tool_name,
                "confidence": round(score, 2),
                "description": description,
                "reason": self._generate_reason(query, tool_name)
            })
        
        return results
    
    def _generate_reason(self, query: str, tool_name: str) -> str:
        """生成推荐理由"""
        if tool_name == "weather":
            return "检测到天气相关关键词"
        elif tool_name == "news":
            return "检测到新闻相关关键词"
        elif tool_name == "calculate":
            return "检测到数学计算相关关键词"
        elif tool_name == "file":
            return "检测到文件操作相关关键词"
        elif tool_name == "search":
            return "需要搜索获取信息"
        elif tool_name == "get_current_time":
            return "检测到时间相关关键词"
        elif tool_name == "image":
            return "检测到图片生成相关关键词"
        elif tool_name == "memory":
            return "检测到记忆相关关键词"
        return "匹配相关工具"
    
    def get_best_tool(self, query: str) -> Optional[str]:
        """获取最佳匹配工具"""
        recommendations = self.recommend_tools(query, top_n=1)
        if recommendations and recommendations[0]["confidence"] > 5:
            return recommendations[0]["tool_name"]
        return None
    
    def should_use_tool(self, query: str) -> bool:
        """判断是否需要使用工具"""
        recommendations = self.recommend_tools(query, top_n=1)
        return len(recommendations) > 0 and recommendations[0]["confidence"] > 10
    
    def explain_decision(self, query: str) -> str:
        """解释工具选择决策"""
        recommendations = self.recommend_tools(query, top_n=3)
        
        if not recommendations:
            return "未匹配到合适的工具，将直接回答问题。"
        
        result = "工具推荐分析：\n"
        for rec in recommendations:
            result += f"- {rec['tool_name']} ({rec['confidence']}%): {rec['description']} - {rec['reason']}\n"
        
        if recommendations[0]["confidence"] > 50:
            result += f"\n将使用 {recommendations[0]['tool_name']} 工具处理此请求。"
        else:
            result += "\n匹配度较低，将直接回答问题。"
        
        return result

# 创建全局实例
tool_recommender = ToolRecommender()

# 便捷函数
def recommend_tool(query: str) -> Optional[str]:
    """推荐工具"""
    return tool_recommender.get_best_tool(query)

def analyze_tools(query: str) -> List[Dict[str, any]]:
    """分析工具匹配"""
    return tool_recommender.recommend_tools(query)
