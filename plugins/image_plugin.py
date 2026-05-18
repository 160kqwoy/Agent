#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图片生成插件 - 使用 DALL-E API"""

import os
import requests
from typing import List
from . import ToolPlugin

class ImagePlugin(ToolPlugin):
    """图片生成插件类"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get("OPENAI_API_KEY", "demo_key")
        self.base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com")
    
    def get_name(self) -> str:
        """返回插件名称"""
        return "image"
    
    def get_description(self) -> str:
        """返回插件描述"""
        return "使用 AI 生成图片"
    
    def get_usage(self) -> str:
        """返回使用说明"""
        return """
使用方法:
1. 生成图片: image generate --prompt <描述> [--size <尺寸>]

支持的尺寸:
- 256x256
- 512x512 (默认)
- 1024x1024

示例:
image generate --prompt 一只可爱的猫咪
image generate --prompt 未来城市风景 --size 1024x1024
        """.strip()
    
    def get_parameters(self) -> List[str]:
        """返回参数列表"""
        return ["prompt", "size"]
    
    def generate(self, prompt: str, size: str = "512x512") -> str:
        """生成图片"""
        # 验证尺寸
        valid_sizes = ["256x256", "512x512", "1024x1024"]
        if size not in valid_sizes:
            size = "512x512"
        
        try:
            url = f"{self.base_url}/v1/images/generations"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "prompt": prompt,
                "n": 1,
                "size": size
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                image_url = result["data"][0]["url"]
                return f"🖼️ 图片生成成功！\n\n描述: {prompt}\n尺寸: {size}\n图片链接: {image_url}"
            else:
                return f"图片生成失败: {response.status_code}"
        except Exception as e:
            return f"图片生成异常: {str(e)}"
    
    def execute(self, *args, **kwargs) -> str:
        """执行工具调用"""
        if args:
            command = args[0]
            if command == "generate":
                prompt = kwargs.get("prompt", "") or kwargs.get("q", "") or (args[1] if len(args) > 1 else "")
                size = kwargs.get("size", "512x512")
                return self.generate(prompt, size)
            else:
                return f"未知命令: {command}"
        return "请提供命令参数"
