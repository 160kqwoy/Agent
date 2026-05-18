#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件操作工具插件
"""

import os
from . import ToolPlugin

class FilePlugin(ToolPlugin):
    """文件操作工具插件"""
    
    def get_name(self) -> str:
        return "file_operations"
    
    def get_description(self) -> str:
        return "文件读写操作"
    
    def get_usage(self) -> str:
        return "当用户需要读取、写入或删除文件时调用此工具"
    
    def get_parameters(self) -> list:
        return ["operation", "file_path", "content"]
    
    def execute(self, operation: str, file_path: str = "", content: str = "") -> str:
        """执行文件操作"""
        operation = operation.lower().strip()
        
        # 安全检查：禁止危险路径
        dangerous_patterns = ["..", "/etc/", "/root/", "C:\\Windows"]
        for pattern in dangerous_patterns:
            if pattern in file_path:
                return f"错误：不允许访问危险路径"
        
        # 确保在当前目录下
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)
        
        try:
            if operation == "read":
                return self._read_file(file_path)
            elif operation == "write":
                return self._write_file(file_path, content)
            elif operation == "delete":
                return self._delete_file(file_path)
            else:
                return f"错误：未知操作 '{operation}'，支持的操作：read, write, delete"
        except Exception as e:
            return f"操作失败: {str(e)}"
    
    def _read_file(self, file_path: str) -> str:
        """读取文件内容"""
        if not os.path.exists(file_path):
            return f"错误：文件 '{file_path}' 不存在"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content) > 500:
                content = content[:500] + "\n...（内容过长，已截断）"
            
            return f"文件内容：\n{content}"
        except UnicodeDecodeError:
            return "错误：无法读取非文本文件"
    
    def _write_file(self, file_path: str, content: str) -> str:
        """写入文件内容"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"文件 '{file_path}' 写入成功"
        except Exception as e:
            return f"写入失败: {str(e)}"
    
    def _delete_file(self, file_path: str) -> str:
        """删除文件"""
        if not os.path.exists(file_path):
            return f"错误：文件 '{file_path}' 不存在"
        
        os.remove(file_path)
        return f"文件 '{file_path}' 删除成功"