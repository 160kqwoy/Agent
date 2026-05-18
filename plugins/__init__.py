#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件系统框架 - 支持动态加载和热更新
"""

import os
import sys
import importlib
import inspect
from typing import Dict, Any, Callable, Optional, List
from abc import ABC, abstractmethod

class Plugin(ABC):
    """插件基类"""
    
    @abstractmethod
    def get_name(self) -> str:
        """获取插件名称"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取插件描述"""
        pass
    
    @abstractmethod
    def get_usage(self) -> str:
        """获取使用说明"""
        pass
    
    @abstractmethod
    def get_parameters(self) -> List[str]:
        """获取参数列表"""
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> str:
        """执行插件"""
        pass

class ToolPlugin(Plugin):
    """工具插件基类"""
    
    def __init__(self):
        self.name = self.get_name()
        self.description = self.get_description()
        self.usage = self.get_usage()
        self.parameters = self.get_parameters()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "usage": self.usage,
            "parameters": self.parameters,
            "function": self.execute
        }

class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Plugin] = {}
        self.loaded_modules: Dict[str, Any] = {}
        
    def load_plugin(self, module_name: str) -> Optional[Plugin]:
        """加载单个插件模块"""
        try:
            # 构建模块路径
            module_path = f"{self.plugin_dir}.{module_name}"
            
            # 如果已加载，先卸载
            if module_path in sys.modules:
                del sys.modules[module_path]
            
            # 动态导入模块
            module = importlib.import_module(module_path)
            
            # 查找 Plugin 子类（排除抽象类）
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Plugin) and obj != Plugin and not inspect.isabstract(obj):
                    # 创建插件实例
                    instance = obj()
                    self.plugins[instance.get_name()] = instance
                    self.loaded_modules[module_path] = module
                    return instance
            
            return None
        except Exception as e:
            print(f"加载插件失败 {module_name}: {str(e)}")
            return None
    
    def load_all_plugins(self) -> List[str]:
        """加载所有插件"""
        loaded = []
        
        # 确保插件目录存在
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            return loaded
        
        # 遍历插件目录
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]  # 去掉 .py
                if self.load_plugin(module_name):
                    loaded.append(module_name)
        
        return loaded
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            return True
        return False
    
    def reload_plugin(self, module_name: str) -> Optional[Plugin]:
        """热更新插件"""
        # 先卸载
        # 查找对应的插件名称
        plugin_to_remove = None
        for name, plugin in self.plugins.items():
            module_path = f"{self.plugin_dir}.{module_name}"
            if module_path in self.loaded_modules:
                plugin_to_remove = name
                break
        
        if plugin_to_remove:
            self.unload_plugin(plugin_to_remove)
        
        # 重新加载
        return self.load_plugin(module_name)
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """获取插件"""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, Plugin]:
        """获取所有插件"""
        return self.plugins
    
    def get_tool_list(self) -> Dict[str, Dict[str, Any]]:
        """获取工具列表（兼容旧版工具格式）"""
        tools = {}
        for name, plugin in self.plugins.items():
            tools[name] = plugin.to_dict()
        return tools

# 创建全局插件管理器实例
plugin_manager = PluginManager()

# 便捷函数
def load_plugins() -> List[str]:
    """加载所有插件"""
    return plugin_manager.load_all_plugins()

def get_plugin(plugin_name: str) -> Optional[Plugin]:
    """获取插件"""
    return plugin_manager.get_plugin(plugin_name)

def get_all_plugins() -> Dict[str, Plugin]:
    """获取所有插件"""
    return plugin_manager.get_all_plugins()

def get_tools_from_plugins() -> Dict[str, Dict[str, Any]]:
    """从插件获取工具列表"""
    return plugin_manager.get_tool_list()

def reload_plugin(module_name: str) -> Optional[Plugin]:
    """热更新插件"""
    return plugin_manager.reload_plugin(module_name)