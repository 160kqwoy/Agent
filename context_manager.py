#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对话上下文管理器"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from collections import defaultdict

class ContextManager:
    """对话上下文管理器"""
    
    def __init__(self):
        # 当前对话上下文
        self.conversations: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        # 实体缓存（存储识别到的实体）
        self.entity_cache: Dict[str, Dict[str, Any]] = defaultdict(dict)
        # 话题跟踪
        self.topic_tracker: Dict[str, Dict[str, Any]] = defaultdict(dict)
        # 意图历史
        self.intent_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    # ========== 对话上下文管理 ==========
    
    def add_message(self, conversation_id: str, role: str, content: str):
        """添加消息到对话上下文"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.conversations[conversation_id].append(message)
        
        # 限制上下文长度（最近20条消息）
        if len(self.conversations[conversation_id]) > 20:
            self.conversations[conversation_id] = self.conversations[conversation_id][-20:]
    
    def get_context(self, conversation_id: str, max_messages: int = 10) -> List[Dict[str, Any]]:
        """获取对话上下文"""
        messages = self.conversations.get(conversation_id, [])
        return messages[-max_messages:]
    
    def get_context_string(self, conversation_id: str, max_messages: int = 10) -> str:
        """获取格式化的上下文字符串"""
        messages = self.get_context(conversation_id, max_messages)
        lines = []
        for msg in messages:
            role = "用户" if msg["role"] == "user" else "助手"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)
    
    def clear_context(self, conversation_id: str):
        """清空对话上下文"""
        self.conversations[conversation_id] = []
        self.entity_cache[conversation_id] = {}
        self.topic_tracker[conversation_id] = {}
    
    # ========== 实体识别与缓存 ==========
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        从文本中提取实体
        
        返回:
            {
                "locations": ["北京", "上海"],
                "dates": ["明天", "下周"],
                "numbers": ["100", "5"],
                "topics": ["天气", "新闻"]
            }
        """
        entities = {
            "locations": [],
            "dates": [],
            "numbers": [],
            "topics": []
        }
        
        # 地点关键词
        location_keywords = ["北京", "上海", "广州", "深圳", "成都", "杭州", "南京", "武汉", "西安", "重庆",
                            "东京", "纽约", "伦敦", "巴黎", "悉尼", "香港", "台北", "澳门"]
        
        # 日期关键词
        date_keywords = ["今天", "明天", "昨天", "前天", "后天", "本周", "下周", "上周",
                        "本月", "下月", "上月", "今年", "明年", "去年", "现在", "最近"]
        
        # 话题关键词
        topic_keywords = {
            "weather": ["天气", "温度", "预报", "下雨", "晴天"],
            "news": ["新闻", "资讯", "头条", "热点"],
            "calculation": ["计算", "多少", "等于"],
            "time": ["时间", "几点", "日期"],
            "image": ["图片", "生成", "照片"],
            "memory": ["记得", "回忆", "之前"]
        }
        
        # 提取地点
        for loc in location_keywords:
            if loc in text:
                entities["locations"].append(loc)
        
        # 提取日期
        for date in date_keywords:
            if date in text:
                entities["dates"].append(date)
        
        # 提取数字
        import re
        numbers = re.findall(r'\d+', text)
        entities["numbers"] = numbers
        
        # 提取话题
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    entities["topics"].append(topic)
                    break
        
        return entities
    
    def update_entity_cache(self, conversation_id: str, text: str):
        """更新实体缓存"""
        entities = self.extract_entities(text)
        
        for entity_type, values in entities.items():
            if values:
                current = self.entity_cache[conversation_id].get(entity_type, [])
                # 添加新实体，去重
                for value in values:
                    if value not in current:
                        current.append(value)
                self.entity_cache[conversation_id][entity_type] = current
    
    def get_entity_cache(self, conversation_id: str) -> Dict[str, List[str]]:
        """获取实体缓存"""
        return self.entity_cache.get(conversation_id, {})
    
    def get_recent_location(self, conversation_id: str) -> Optional[str]:
        """获取最近提到的地点"""
        entities = self.get_entity_cache(conversation_id)
        locations = entities.get("locations", [])
        return locations[-1] if locations else None
    
    # ========== 意图识别 ==========
    
    def recognize_intent(self, text: str) -> Dict[str, float]:
        """
        识别用户意图
        
        返回:
            {"intent_name": confidence}
        """
        intents = {
            "weather_query": {
                "keywords": ["天气", "温度", "预报", "下雨", "晴天", "多云", "气温"],
                "weight": 2.0
            },
            "news_query": {
                "keywords": ["新闻", "资讯", "头条", "热点", "报道"],
                "weight": 1.5
            },
            "calculation": {
                "keywords": ["计算", "加", "减", "乘", "除", "等于", "多少"],
                "weight": 2.0
            },
            "time_query": {
                "keywords": ["时间", "几点", "现在", "日期", "星期"],
                "weight": 2.0
            },
            "image_generation": {
                "keywords": ["图片", "生成", "照片", "画图"],
                "weight": 1.5
            },
            "text_processing": {
                "keywords": ["摘要", "总结", "关键词", "翻译", "拼音"],
                "weight": 1.5
            },
            "data_conversion": {
                "keywords": ["换算", "转换", "进制", "单位"],
                "weight": 1.5
            },
            "memory_access": {
                "keywords": ["记得", "回忆", "之前", "历史"],
                "weight": 1.0
            },
            "general_chat": {
                "keywords": ["你好", "谢谢", "再见", "聊天", "话题"],
                "weight": 1.0
            }
        }
        
        results = {}
        text_lower = text.lower()
        
        for intent_name, config in intents.items():
            score = 0.0
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    score += 1.0
            
            if score > 0:
                normalized_score = (score / len(config["keywords"])) * 100 * config["weight"]
                results[intent_name] = round(normalized_score, 2)
        
        # 按分数排序
        sorted_results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True))
        return sorted_results
    
    def track_intent(self, conversation_id: str, text: str):
        """跟踪意图历史"""
        intent_result = self.recognize_intent(text)
        
        if intent_result:
            top_intent = next(iter(intent_result))
            self.intent_history[conversation_id].append({
                "intent": top_intent,
                "confidence": intent_result[top_intent],
                "text": text,
                "timestamp": datetime.now().isoformat()
            })
    
    def get_intent_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """获取意图历史"""
        return self.intent_history.get(conversation_id, [])
    
    def get_current_intent(self, conversation_id: str) -> Optional[str]:
        """获取当前意图"""
        history = self.get_intent_history(conversation_id)
        if history:
            return history[-1]["intent"]
        return None
    
    # ========== 话题跟踪 ==========
    
    def track_topic(self, conversation_id: str, topic: str, confidence: float = 1.0):
        """跟踪当前话题"""
        self.topic_tracker[conversation_id] = {
            "topic": topic,
            "confidence": confidence,
            "updated_at": datetime.now().isoformat()
        }
    
    def get_current_topic(self, conversation_id: str) -> Optional[str]:
        """获取当前话题"""
        topic_data = self.topic_tracker.get(conversation_id, {})
        return topic_data.get("topic")
    
    def infer_topic(self, conversation_id: str) -> str:
        """根据对话历史推断当前话题"""
        context = self.get_context(conversation_id)
        if not context:
            return "general"
        
        # 分析最近几条消息的意图
        intents = []
        for msg in context[-3:]:
            if msg["role"] == "user":
                intent_result = self.recognize_intent(msg["content"])
                if intent_result:
                    intents.append(next(iter(intent_result)))
        
        # 返回出现次数最多的意图作为话题
        if intents:
            from collections import Counter
            counter = Counter(intents)
            return counter.most_common(1)[0][0]
        
        return "general"
    
    # ========== 上下文理解 ==========
    
    def resolve_references(self, conversation_id: str, text: str) -> str:
        """
        解析指代关系
        
        将"它"、"这个"、"那里"等指代词替换为具体内容
        """
        context = self.get_context(conversation_id)
        if not context:
            return text
        
        # 简单的指代解析规则
        references = {
            "它": self._find_last_noun(context),
            "这个": self._find_last_noun(context),
            "那个": self._find_last_noun(context),
            "那里": self.get_recent_location(conversation_id),
            "那里的": self.get_recent_location(conversation_id),
            "这里": self.get_recent_location(conversation_id)
        }
        
        resolved_text = text
        for ref, replacement in references.items():
            if ref in text and replacement:
                resolved_text = resolved_text.replace(ref, replacement)
        
        return resolved_text
    
    def _find_last_noun(self, context: List[Dict[str, Any]]) -> Optional[str]:
        """从上下文中查找最近提到的名词"""
        # 常见名词列表
        common_nouns = ["天气", "新闻", "图片", "结果", "问题", "答案", "信息", "数据", "时间"]
        
        for msg in reversed(context):
            content = msg["content"]
            for noun in common_nouns:
                if noun in content:
                    return noun
        return None
    
    def detect_topic_change(self, conversation_id: str, text: str) -> bool:
        """检测话题是否发生变化"""
        current_topic = self.get_current_topic(conversation_id)
        if not current_topic:
            return False
        
        new_intent = self.recognize_intent(text)
        if not new_intent:
            return False
        
        new_topic = next(iter(new_intent))
        return new_topic != current_topic
    
    # ========== 摘要生成 ==========
    
    def generate_context_summary(self, conversation_id: str) -> str:
        """生成对话上下文摘要"""
        context = self.get_context(conversation_id)
        if not context:
            return "暂无对话历史"
        
        # 获取实体信息
        entities = self.get_entity_cache(conversation_id)
        locations = entities.get("locations", [])
        dates = entities.get("dates", [])
        
        # 获取意图历史
        intent_history = self.get_intent_history(conversation_id)
        recent_intents = [item["intent"] for item in intent_history[-3:]]
        
        # 构建摘要
        summary_parts = []
        
        if locations:
            summary_parts.append(f"讨论地点: {', '.join(locations)}")
        
        if dates:
            summary_parts.append(f"讨论时间: {', '.join(dates)}")
        
        if recent_intents:
            summary_parts.append(f"最近意图: {', '.join(recent_intents)}")
        
        current_topic = self.infer_topic(conversation_id)
        summary_parts.append(f"当前话题: {current_topic}")
        
        return "\n".join(summary_parts)

# 创建全局实例
context_manager = ContextManager()

# 便捷函数
def get_conversation_context(conversation_id: str, max_messages: int = 10) -> str:
    """获取对话上下文字符串"""
    return context_manager.get_context_string(conversation_id, max_messages)

def update_conversation_context(conversation_id: str, role: str, content: str):
    """更新对话上下文"""
    context_manager.add_message(conversation_id, role, content)
    context_manager.update_entity_cache(conversation_id, content)
    context_manager.track_intent(conversation_id, content)
    
    # 更新话题
    topic = context_manager.infer_topic(conversation_id)
    context_manager.track_topic(conversation_id, topic)

def resolve_references_in_text(conversation_id: str, text: str) -> str:
    """解析文本中的指代关系"""
    return context_manager.resolve_references(conversation_id, text)

def get_conversation_summary(conversation_id: str) -> str:
    """获取对话摘要"""
    return context_manager.generate_context_summary(conversation_id)
