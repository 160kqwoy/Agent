#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文本处理工具插件"""

from collections import Counter
from typing import List, Dict
from . import ToolPlugin

class TextProcessorPlugin(ToolPlugin):
    """文本处理工具插件类"""
    
    def __init__(self):
        super().__init__()
    
    def get_name(self) -> str:
        """返回插件名称"""
        return "text"
    
    def get_description(self) -> str:
        """返回插件描述"""
        return "文本处理工具（摘要、关键词提取、格式转换）"
    
    def get_usage(self) -> str:
        """返回使用说明"""
        return """
使用方法:
1. 文本摘要: text summarize --text <文本内容> [--length <长度>]
2. 关键词提取: text keywords --text <文本内容> [--count <数量>]
3. 格式转换: text convert --text <文本内容> --from <格式> --to <格式>
4. 拼音转换: text pinyin --text <文本内容>

支持的格式转换:
- markdown -> plain (Markdown转纯文本)
- html -> plain (HTML转纯文本)
- plain -> markdown (纯文本转Markdown)

示例:
text summarize --text "这是一段很长的文本..."
text keywords --text "人工智能技术发展迅速" --count 5
text convert --text "# 标题" --from markdown --to plain
text pinyin --text "你好世界"
        """.strip()
    
    def get_parameters(self) -> List[str]:
        """返回参数列表"""
        return ["text", "length", "count", "from", "to"]
    
    def summarize(self, text: str, max_length: int = 100) -> str:
        """
        提取文本摘要
        
        算法：
        1. 分割句子
        2. 计算每个句子的重要性（基于词频）
        3. 选择最重要的句子
        """
        if not text:
            return "请提供要摘要的文本"
        
        # 分割句子
        sentences = []
        for sep in ['。', '！', '？', '.', '!', '?', '\n', ';', '；']:
            if sep == '\n':
                parts = text.split(sep)
            else:
                parts = text.replace(sep, '|||').split('|||')
            sentences.extend([s.strip() for s in parts if s.strip()])
        
        if not sentences:
            sentences = [text]
        
        # 计算词频
        words = []
        for sent in sentences:
            words.extend(self._extract_words(sent))
        
        word_counts = Counter(words)
        
        # 计算句子得分
        sentence_scores = []
        for i, sent in enumerate(sentences):
            score = 0
            sent_words = self._extract_words(sent)
            for word in sent_words:
                score += word_counts.get(word, 0)
            # 位置权重：开头的句子更重要
            position_weight = 1.0 if i < len(sentences) // 3 else 0.7
            sentence_scores.append((i, sent, score * position_weight))
        
        # 按得分排序
        sentence_scores.sort(key=lambda x: x[2], reverse=True)
        
        # 选择最重要的句子，确保不超过最大长度
        result = []
        current_length = 0
        for _, sent, _ in sentence_scores:
            if current_length + len(sent) <= max_length:
                result.append(sent)
                current_length += len(sent) + 1  # +1 for separator
            else:
                break
        
        if not result:
            return text[:max_length] + "..."
        
        return "。".join(result) + "。"
    
    def _extract_words(self, text: str) -> List[str]:
        """提取中文词语"""
        import re
        # 移除标点符号
        text = re.sub(r'[^\w\s]', '', text)
        # 简单分词（按字符）
        return list(text)
    
    def extract_keywords(self, text: str, top_n: int = 5) -> str:
        """提取关键词"""
        if not text:
            return "请提供要提取关键词的文本"
        
        # 移除标点符号和空白
        import re
        clean_text = re.sub(r'[^\w\s]', '', text)
        words = clean_text.split()
        
        if not words:
            words = list(text)
        
        # 计算词频
        word_counts = Counter(words)
        
        # 获取TOP N关键词
        top_words = word_counts.most_common(top_n)
        
        if not top_words:
            return "未找到关键词"
        
        result = "关键词列表:\n"
        for i, (word, count) in enumerate(top_words, 1):
            result += f"{i}. {word} (出现{count}次)\n"
        
        return result.strip()
    
    def convert_format(self, text: str, from_format: str, to_format: str) -> str:
        """
        文本格式转换
        
        支持的格式:
        - markdown -> plain
        - html -> plain
        - plain -> markdown
        """
        if not text:
            return "请提供要转换的文本"
        
        from_format = from_format.lower()
        to_format = to_format.lower()
        
        if from_format == "markdown" and to_format == "plain":
            return self._markdown_to_plain(text)
        elif from_format == "html" and to_format == "plain":
            return self._html_to_plain(text)
        elif from_format == "plain" and to_format == "markdown":
            return self._plain_to_markdown(text)
        else:
            return f"不支持从 {from_format} 转换到 {to_format}"
    
    def _markdown_to_plain(self, text: str) -> str:
        """Markdown转纯文本"""
        import re
        # 移除标题符号
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        # 移除粗体和斜体
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        # 移除链接
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # 移除图片
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
        # 移除代码块标记
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        # 移除换行
        text = text.replace('\n', ' ')
        return text.strip()
    
    def _html_to_plain(self, text: str) -> str:
        """HTML转纯文本"""
        import re
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 处理HTML实体
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        return text.strip()
    
    def _plain_to_markdown(self, text: str) -> str:
        """纯文本转Markdown"""
        # 简单转换：按段落分割
        paragraphs = text.split('\n\n')
        result = []
        for i, para in enumerate(paragraphs):
            if i == 0 and len(para) < 50:
                # 第一段可能是标题
                result.append(f"# {para}")
            else:
                result.append(para)
        return '\n\n'.join(result)
    
    def to_pinyin(self, text: str) -> str:
        """中文转拼音"""
        try:
            from xpinyin import Pinyin
            p = Pinyin()
            return p.get_pinyin(text, '')
        except ImportError:
            return self._simple_pinyin(text)
    
    def _simple_pinyin(self, text: str) -> str:
        """简单拼音转换（备用方案）"""
        # 常用字拼音映射
        pinyin_map = {
            '你': 'ni', '好': 'hao', '世': 'shi', '界': 'jie',
            '中': 'zhong', '国': 'guo', '人': 'ren', '民': 'min',
            '天': 'tian', '气': 'qi', '今': 'jin', '天': 'tian',
            '明': 'ming', '日': 'ri', '星': 'xing', '期': 'qi',
            '上': 'shang', '海': 'hai', '北': 'bei', '京': 'jing',
            '广': 'guang', '东': 'dong', '深': 'shen', '圳': 'zhen'
        }
        result = []
        for char in text:
            result.append(pinyin_map.get(char, char))
        return ''.join(result)
    
    def execute(self, *args, **kwargs) -> str:
        """执行工具调用"""
        if args:
            command = args[0]
            
            if command == "summarize":
                text = kwargs.get("text", "") or kwargs.get("q", "") or (args[1] if len(args) > 1 else "")
                length = int(kwargs.get("length", "100"))
                return self.summarize(text, length)
            
            elif command == "keywords":
                text = kwargs.get("text", "") or kwargs.get("q", "") or (args[1] if len(args) > 1 else "")
                count = int(kwargs.get("count", "5"))
                return self.extract_keywords(text, count)
            
            elif command == "convert":
                text = kwargs.get("text", "") or (args[1] if len(args) > 1 else "")
                from_format = kwargs.get("from", "") or (args[2] if len(args) > 2 else "")
                to_format = kwargs.get("to", "") or (args[3] if len(args) > 3 else "")
                return self.convert_format(text, from_format, to_format)
            
            elif command == "pinyin":
                text = kwargs.get("text", "") or kwargs.get("q", "") or (args[1] if len(args) > 1 else "")
                return self.to_pinyin(text)
            
            else:
                return f"未知命令: {command}"
        
        return self.get_usage()
