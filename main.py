#!/usr/bin/env python3
"""
AI Agent 骨架代码 - 使用 LangChain 和本地 LLM

功能特性:
- 使用本地 LLM（如 Qwen3.5）作为核心模型
- 集成计算器工具（执行数学运算）
- 集成时间工具（获取当前时间）
- 支持对话记忆
- 实现 ReAct 循环（思考-行动-观察）
"""

import os
import math
import re
import json
import logging
import requests
from datetime import datetime, date
from typing import List, Dict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# 加载环境变量
load_dotenv()

# ==================== 插件系统集成 ====================
from plugins import (
    load_plugins,
    get_tools_from_plugins,
    reload_plugin
)

# ==================== 错误恢复机制 ====================
from error_recovery import (
    execute_with_retry_and_failover
)

# ==================== 性能监控 ====================
from performance_monitor import (
    monitor_performance
)

# ==================== 配置管理系统 ====================

class ConfigManager:
    """配置管理器 - 支持配置文件和环境变量"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        config = {
            # 默认配置
            "history": {
                "file": "chat_history.json",
                "max_size": 50
            },
            "logging": {
                "level": "INFO",
                "file": "agent.log"
            },
            "llm": {
                "base_url": None,
                "model": None,
                "api_key": None,
                "temperature": 0,
                "max_tokens": 2048
            },
            "agent": {
                "max_iterations": 5,
                "history_length": 10
            }
        }
        
        # 从配置文件加载
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    config = self._deep_merge(config, file_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        
        # 从环境变量覆盖
        self._load_from_env(config)
        
        return config
    
    def _deep_merge(self, base: dict, override: dict) -> dict:
        """深度合并配置"""
        result = base.copy()
        for key, value in override.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _load_from_env(self, config: dict):
        """从环境变量加载配置"""
        # 历史配置
        if os.getenv("HISTORY_FILE"):
            config["history"]["file"] = os.getenv("HISTORY_FILE")
        if os.getenv("MAX_HISTORY_SIZE"):
            config["history"]["max_size"] = int(os.getenv("MAX_HISTORY_SIZE"))
        
        # 日志配置
        if os.getenv("LOG_LEVEL"):
            config["logging"]["level"] = os.getenv("LOG_LEVEL")
        if os.getenv("LOG_FILE"):
            config["logging"]["file"] = os.getenv("LOG_FILE")
        
        # LLM 配置
        if os.getenv("LLM_BASE_URL"):
            config["llm"]["base_url"] = os.getenv("LLM_BASE_URL")
        if os.getenv("LLM_MODEL"):
            config["llm"]["model"] = os.getenv("LLM_MODEL")
        if os.getenv("LLM_API_KEY"):
            config["llm"]["api_key"] = os.getenv("LLM_API_KEY")
        if os.getenv("LLM_TEMPERATURE"):
            config["llm"]["temperature"] = float(os.getenv("LLM_TEMPERATURE"))
        if os.getenv("LLM_MAX_TOKENS"):
            config["llm"]["max_tokens"] = int(os.getenv("LLM_MAX_TOKENS"))
        
        # Agent 配置
        if os.getenv("MAX_ITERATIONS"):
            config["agent"]["max_iterations"] = int(os.getenv("MAX_ITERATIONS"))
        if os.getenv("HISTORY_LENGTH"):
            config["agent"]["history_length"] = int(os.getenv("HISTORY_LENGTH"))
    
    def get(self, key: str, default=None):
        """获取配置值，支持点路径如 'history.file'"""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value):
        """设置配置值，支持点路径"""
        keys = key.split('.')
        config = self.config
        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get_config_summary(self) -> str:
        """获取配置摘要（隐藏敏感信息）"""
        summary = "配置摘要:\n"
        summary += f"- 历史文件: {self.get('history.file')}\n"
        summary += f"- 最大历史条数: {self.get('history.max_size')}\n"
        summary += f"- 日志级别: {self.get('logging.level')}\n"
        summary += f"- 日志文件: {self.get('logging.file')}\n"
        summary += f"- LLM 模型: {self.get('llm.model')}\n"
        summary += f"- LLM 基础URL: {self.get('llm.base_url')}\n"
        summary += f"- API Key: {'***' if self.get('llm.api_key') else '未设置'}\n"
        summary += f"- 最大推理轮数: {self.get('agent.max_iterations')}\n"
        return summary


# 初始化配置管理器
config_manager = ConfigManager()

# 从配置获取常用值
HISTORY_FILE = config_manager.get("history.file", "chat_history.json")
MAX_HISTORY_SIZE = config_manager.get("history.max_size", 50)
MAX_ITERATIONS = config_manager.get("agent.max_iterations", 5)
HISTORY_LENGTH = config_manager.get("agent.history_length", 10)

# ==================== 日志系统 ====================

def setup_logging():
    """配置日志系统"""
    log_level = config_manager.get("logging.level", "INFO").upper()
    log_file = config_manager.get("logging.file", "agent.log")
    
    # 创建日志记录器
    logger = logging.getLogger("AI_AGENT")
    logger.setLevel(log_level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# 初始化日志记录器
logger = setup_logging()


def log_info(message: str):
    """记录信息日志"""
    logger.info(message)


def log_debug(message: str):
    """记录调试日志"""
    logger.debug(message)


def log_error(message: str):
    """记录错误日志"""
    logger.error(message)


def log_tool_call(tool_name: str, params: str, result: str):
    """记录工具调用"""
    logger.info(f"工具调用: {tool_name}({params}) -> {result[:50]}..." if len(result) > 50 else f"工具调用: {tool_name}({params}) -> {result}")


def log_user_input(user_input: str):
    """记录用户输入"""
    logger.info(f"用户输入: {user_input[:50]}..." if len(user_input) > 50 else f"用户输入: {user_input}")


def log_response(response: str):
    """记录响应"""
    logger.info(f"Agent 响应: {response[:50]}..." if len(response) > 50 else f"Agent 响应: {response}")


def get_current_time():
    """获取当前时间"""
    now = datetime.now()
    # weekday() 返回 0-6 对应周一到周日
    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')}，星期{weekdays[date.today().weekday()]}"


def calculate(expression):
    """执行数学运算"""
    try:
        allowed_locals = {
            'math': math,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'exp': math.exp,
            'pow': pow,
            'abs': abs,
            'round': round,
        }
        
        safe_expression = expression.replace('__', '').replace('import', '').replace('exec', '').replace('eval', '')
        result = eval(safe_expression, {"__builtins__": {}}, allowed_locals)
        return f"计算结果: {result}"
    
    except Exception as e:
        return f"计算错误: {str(e)}"


def read_file(file_path):
    """读取本地文本文件内容"""
    try:
        # 安全检查：防止路径遍历攻击
        file_path = os.path.normpath(file_path)
        
        # 检查路径是否包含危险字符
        if '..' in file_path or '\\' in file_path or '/' in file_path:
            return "错误：不允许访问上级目录或使用路径分隔符"
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"错误：文件 '{file_path}' 不存在"
        
        # 检查是否为文件（不是目录）
        if not os.path.isfile(file_path):
            return f"错误：'{file_path}' 不是一个文件"
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 限制返回内容长度
        max_length = 2000
        if len(content) > max_length:
            content = content[:max_length] + f"\n\n（内容已截断，文件共 {len(content)} 字符）"
        
        return f"文件内容:\n{content}"
    
    except UnicodeDecodeError:
        return f"错误：无法以 UTF-8 编码读取文件 '{file_path}'，可能是二进制文件"
    except Exception as e:
        return f"读取文件失败: {str(e)}"


def write_file(file_path, content):
    """创建或写入文件"""
    try:
        # 安全检查：防止路径遍历攻击
        file_path = os.path.normpath(file_path)
        
        # 检查路径是否包含危险字符
        if '..' in file_path or '\\' in file_path or '/' in file_path:
            return "错误：不允许访问上级目录或使用路径分隔符"
        
        # 检查文件名是否合法
        if not file_path or len(file_path) > 255:
            return "错误：文件名无效或过长"
        
        # 检查内容长度限制
        max_content_length = 10000
        if len(content) > max_content_length:
            return f"错误：内容过长，最大支持 {max_content_length} 字符"
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"文件 '{file_path}' 已成功创建，内容为:\n{content}"
    
    except Exception as e:
        return f"写入文件失败: {str(e)}"


def delete_file(file_path):
    """删除文件"""
    try:
        # 安全检查：防止路径遍历攻击
        file_path = os.path.normpath(file_path)
        
        # 检查路径是否包含危险字符
        if '..' in file_path or '\\' in file_path or '/' in file_path:
            return "错误：不允许访问上级目录或使用路径分隔符"
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"错误：文件 '{file_path}' 不存在"
        
        # 检查是否为文件（不是目录）
        if not os.path.isfile(file_path):
            return f"错误：'{file_path}' 不是一个文件"
        
        # 删除文件
        os.remove(file_path)
        
        return f"文件 '{file_path}' 已成功删除"
    
    except Exception as e:
        return f"删除文件失败: {str(e)}"


# ==================== 安全输入过滤 ====================

class InputSecurityFilter:
    """输入安全过滤器 - 检测和过滤恶意输入"""
    
    # SQL 注入模式
    SQL_INJECTION_PATTERNS = [
        r"('|\")\s*OR\s*1\s*=\s*1",
        r"('|\")\s*UNION\s*SELECT",
        r"('|\")\s*DROP\s*TABLE",
        r"('|\")\s*DELETE\s*FROM",
        r"('|\")\s*INSERT\s*INTO",
        r"('|\")\s*UPDATE\s*.*\s*SET",
        r"--.*",
        r";\s*DROP\s*TABLE",
        r";\s*DELETE\s*FROM",
        r"'?\s*AND\s*1\s*=\s*1",
        r"'?\s*OR\s*'x'\s*=\s*'x",
        r"EXEC\s+\(?",
        r"sp_",
        r"xp_",
    ]
    
    # 命令注入模式
    COMMAND_INJECTION_PATTERNS = [
        r";\s*(ls|dir|rm|del|cp|mv|mkdir|rmdir)",
        r";\s*(cat|type|more|less|head|tail)",
        r";\s*(python|python3|node|java|ruby)",
        r";\s*(curl|wget|ftp|ssh)",
        r";\s*(chmod|chown|sudo|su)",
        r"\|\s*(ls|dir|rm|del|cat|type)",
        r"\$\(.*\)",
        r"`.*`",
        r">>\s*\/",
        r"<\s*\/",
    ]
    
    # 敏感信息模式
    SENSITIVE_PATTERNS = [
        r"API[_-]?KEY\s*[=:]\s*[A-Za-z0-9]+",
        r"API[_-]?KEY\s+[是为]\s*[A-Za-z0-9]+",
        r"api[_-]?key\s*[=:]\s*[A-Za-z0-9]+",
        r"api[_-]?key\s+[是为]\s*[A-Za-z0-9]+",
        r"SECRET\s*[=:]\s*[A-Za-z0-9]+",
        r"secret\s*[=:]\s*[A-Za-z0-9]+",
        r"PASSWORD\s*[=:]\s*[A-Za-z0-9]+",
        r"password\s*[=:]\s*[A-Za-z0-9]+",
        r"token\s*[=:]\s*[A-Za-z0-9]+",
        r"TOKEN\s*[=:]\s*[A-Za-z0-9]+",
        r"ssh\s*key\s*[=:]",
        r"私钥|private\s*key",
    ]
    
    # 危险路径模式
    DANGEROUS_PATH_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"(?<!\.)\.\.(?=/)",
        r"(?<!\.)\.\.(?=\\)",
        r"/etc/",
        r"/root/",
        r"C:\\Windows\\",
        r"C:\\Users\\",
        r"/home/",
        r"\\boot\\",
        r"/boot/",
    ]
    
    def __init__(self, max_length: int = 2000):
        self.max_length = max_length
    
    def detect_sql_injection(self, input_text: str) -> bool:
        """检测 SQL 注入攻击"""
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_text, re.IGNORECASE):
                return True
        return False
    
    def detect_command_injection(self, input_text: str) -> bool:
        """检测命令注入攻击"""
        for pattern in self.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, input_text, re.IGNORECASE):
                return True
        return False
    
    def detect_sensitive_info(self, input_text: str) -> bool:
        """检测敏感信息"""
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, input_text, re.IGNORECASE):
                return True
        return False
    
    def detect_dangerous_path(self, input_text: str) -> bool:
        """检测危险路径访问"""
        for pattern in self.DANGEROUS_PATH_PATTERNS:
            if re.search(pattern, input_text, re.IGNORECASE):
                return True
        return False
    
    def is_too_long(self, input_text: str) -> bool:
        """检查输入是否过长"""
        return len(input_text) > self.max_length
    
    def sanitize_input(self, input_text: str) -> str:
        """清理输入，移除潜在危险字符"""
        # 移除 null 字符
        sanitized = input_text.replace('\x00', '')
        
        # 移除控制字符（保留基本的换行和制表符）
        sanitized = ''.join(c for c in sanitized if ord(c) >= 32 or c in '\n\t')
        
        return sanitized
    
    def validate_input(self, input_text: str) -> dict:
        """验证输入是否安全"""
        result = {
            "is_safe": True,
            "errors": [],
            "warnings": []
        }
        
        # 检查长度
        if self.is_too_long(input_text):
            result["is_safe"] = False
            result["errors"].append(f"输入过长（最大 {self.max_length} 字符）")
        
        # 检测 SQL 注入
        if self.detect_sql_injection(input_text):
            result["is_safe"] = False
            result["errors"].append("检测到 SQL 注入攻击")
        
        # 检测命令注入
        if self.detect_command_injection(input_text):
            result["is_safe"] = False
            result["errors"].append("检测到命令注入攻击")
        
        # 检测危险路径
        if self.detect_dangerous_path(input_text):
            result["is_safe"] = False
            result["errors"].append("检测到危险路径访问")
        
        # 检测敏感信息（警告而非阻止）
        if self.detect_sensitive_info(input_text):
            result["warnings"].append("检测到潜在敏感信息")
        
        return result


# 初始化安全过滤器
security_filter = InputSecurityFilter()


def validate_user_input(user_input: str) -> dict:
    """验证用户输入的安全函数"""
    return security_filter.validate_input(user_input)


def sanitize_user_input(user_input: str) -> str:
    """清理用户输入"""
    return security_filter.sanitize_input(user_input)


# ==================== 网络搜索工具 ====================

def web_search(query: str, max_results: int = 5) -> str:
    """
    使用 DuckDuckGo 进行网络搜索
    :param query: 搜索关键词
    :param max_results: 最大返回结果数
    :return: 搜索结果摘要
    """
    try:
        # DuckDuckGo 搜索 API
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_redirect": 1,
            "no_html": 1,
            "skip_disambig": 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 整理搜索结果
        results = []
        
        # 首先检查 Instant Answer
        if "AbstractText" in data and data["AbstractText"]:
            results.append(f"【快速回答】\n{data['AbstractText']}")
            if "AbstractURL" in data and data["AbstractURL"]:
                results[-1] += f"\n来源: {data['AbstractURL']}"
        
        # 添加搜索结果
        if "Results" in data and data["Results"]:
            for i, result in enumerate(data["Results"][:max_results], 1):
                title = result.get("Text", "")
                url = result.get("FirstURL", "")
                description = result.get("Description", "")
                
                if title or description:
                    result_str = f"\n【结果 {i}】\n标题: {title}"
                    if description:
                        result_str += f"\n摘要: {description}"
                    if url:
                        result_str += f"\n链接: {url}"
                    results.append(result_str)
        
        # 如果没有结果，尝试从 RelatedTopics 获取
        if not results and "RelatedTopics" in data and data["RelatedTopics"]:
            for i, topic in enumerate(data["RelatedTopics"][:max_results], 1):
                if isinstance(topic, dict):
                    text = topic.get("Text", "")
                    url = topic.get("FirstURL", "")
                    if text:
                        result_str = f"\n【相关话题 {i}】\n{text}"
                        if url:
                            result_str += f"\n链接: {url}"
                        results.append(result_str)
        
        if not results:
            return f"未找到关于 '{query}' 的搜索结果"
        
        return "\n".join(results)[:3000]  # 限制长度
    
    except requests.exceptions.RequestException as e:
        return f"搜索失败: {str(e)}"
    except Exception as e:
        return f"搜索异常: {str(e)}"


# ==================== 对话历史持久化 ====================

def load_chat_history() -> List[Dict[str, str]]:
    """从文件加载对话历史"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
                # 确保格式正确
                if isinstance(history, list):
                    return history[:MAX_HISTORY_SIZE]
                else:
                    return []
        return []
    except Exception as e:
        print(f"加载对话历史失败: {str(e)}")
        return []


def save_chat_history(history: List[Dict[str, str]]) -> None:
    """保存对话历史到文件"""
    try:
        # 限制历史记录数量
        trimmed_history = history[-MAX_HISTORY_SIZE:]
        
        # 添加时间戳
        for item in trimmed_history:
            if 'timestamp' not in item:
                item['timestamp'] = datetime.now().isoformat()
        
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(trimmed_history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存对话历史失败: {str(e)}")


def clear_chat_history() -> str:
    """清空对话历史"""
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        return "对话历史已清空"
    except Exception as e:
        return f"清空对话历史失败: {str(e)}"


def get_history_summary() -> str:
    """获取对话历史摘要"""
    history = load_chat_history()
    if not history:
        return "暂无对话历史"
    
    summary = f"共有 {len(history)} 条对话记录\n"
    summary += "最近5条记录:\n"
    
    for i, item in enumerate(reversed(history[-5:]), 1):
        user_input = item.get('user', '')[:30] + '...' if len(item.get('user', '')) > 30 else item.get('user', '')
        summary += f"{i}. 用户: {user_input}\n"
    
    return summary


def create_agent():
    """创建 AI Agent 实例"""
    llm_base_url = config_manager.get("llm.base_url")
    llm_model = config_manager.get("llm.model")
    llm_api_key = config_manager.get("llm.api_key")
    llm_temperature = config_manager.get("llm.temperature", 0)
    llm_max_tokens = config_manager.get("llm.max_tokens", 2048)
    
    if not llm_base_url:
        raise EnvironmentError("未设置 LLM_BASE_URL（环境变量或配置文件）")
    if not llm_model:
        raise EnvironmentError("未设置 LLM_MODEL（环境变量或配置文件）")
    if not llm_api_key:
        raise EnvironmentError("未设置 LLM_API_KEY（环境变量或配置文件）")

    llm = ChatOpenAI(
        model_name=llm_model,
        temperature=llm_temperature,
        api_key=llm_api_key,
        base_url=llm_base_url,
        max_tokens=llm_max_tokens
    )

    return llm


# 工具注册表 - 支持从插件系统动态加载
TOOLS = {}

def load_tools():
    """加载工具（从插件系统和内置工具）"""
    global TOOLS
    
    # 清空现有工具
    TOOLS = {}
    
    # 从插件系统加载工具
    plugin_tools = get_tools_from_plugins()
    TOOLS.update(plugin_tools)
    
    # 添加内置工具（历史记录相关）
    TOOLS.update({
        "get_history_summary": {
            "name": "get_history_summary",
            "description": "获取对话历史摘要，显示最近的对话记录",
            "usage": "当用户询问历史记录、查看对话历史或回顾之前的对话时调用此工具",
            "parameters": [],
            "function": get_history_summary
        },
        "clear_chat_history": {
            "name": "clear_chat_history",
            "description": "清空所有对话历史记录",
            "usage": "当用户要求清空历史、重置对话或删除记录时调用此工具",
            "parameters": [],
            "function": clear_chat_history
        }
    })
    
    log_info(f"已加载 {len(TOOLS)} 个工具")
    return TOOLS

def refresh_tools() -> int:
    """刷新工具列表（热更新）"""
    load_tools()
    return len(TOOLS)

def load_plugins_and_tools() -> int:
    """加载插件并初始化工具列表"""
    # 加载所有插件
    plugins = load_plugins()
    log_info(f"已加载 {len(plugins)} 个插件: {plugins}")
    
    # 加载工具
    load_tools()
    
    return len(TOOLS)


def get_tool_list_description():
    """生成工具列表描述，用于提示词"""
    tool_descriptions = []
    for tool_name, tool_info in TOOLS.items():
        params = ", ".join(tool_info["parameters"])
        tool_descriptions.append(
            f"- {tool_name}: {tool_info['description']} (参数: {params})"
        )
    return "\n".join(tool_descriptions)


def extract_tool_call(response):
    """从响应中提取工具调用"""
    # 尝试匹配各种工具调用格式
    patterns = [
        r'工具调用:\s*(\w+)\s*\(\s*(.+?)\s*\)',
        r'行动:\s*(\w+)\s*行动输入:\s*(.+?)(?=\n|$)',
        r'Action:\s*(\w+)\s*Action\s*Input:\s*(.+?)(?=\n|$)',
        r'{"name":"(\w+)","parameters":(.+?)}',
        r'\[(\w+)\]\s*(.+?)(?=\[|\n|$)',
        r'(\w+)\s*\(\s*(.+?)\s*\)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip(), match.group(2).strip()
    
    return None, None


def parse_tool_parameters(tool_name, params_str):
    """解析工具参数"""
    tool_info = TOOLS.get(tool_name)
    if not tool_info:
        return None
    
    expected_params = tool_info["parameters"]
    
    # 如果不需要参数
    if not expected_params:
        return []
    
    # 尝试解析参数
    params = []
    
    # 尝试解析引号内的内容
    quoted_pattern = r'"([^"]+)"|\'([^\']+)\'|(\S+)'
    matches = re.findall(quoted_pattern, params_str)
    
    for match in matches:
        # 优先选择引号内的内容
        param = match[0] or match[1] or match[2]
        if param:
            params.append(param.strip())
    
    return params[:len(expected_params)]


@monitor_performance(key="tool_calls")
def call_tool(tool_name, parameters):
    """调用工具（支持错误恢复和性能监控）"""
    tool_info = TOOLS.get(tool_name)
    if not tool_info:
        return f"错误：未知工具 '{tool_name}'"
    
    def execute_tool():
        """执行工具函数"""
        try:
            func = tool_info["function"]
            return func(*parameters)
        except Exception as e:
            # 返回错误消息，便于错误恢复机制处理
            return f"错误：{str(e)}"
    
    # 使用错误恢复机制执行
    result = execute_with_retry_and_failover(
        execute_tool,
        func_name=tool_name,
        max_retries=2
    )
    
    return result


def build_agent_prompt(user_input, chat_history, tool_results=""):
    """构建 Agent 的系统提示词（支持多轮推理）"""
    tool_list = get_tool_list_description()
    
    prompt = f"""
你是一个智能助手，拥有访问以下工具的能力：

可用工具列表：
{tool_list}

思考-行动-观察-总结流程：
1. 思考：分析用户问题，判断是否需要调用工具，是否需要多步操作
2. 行动：如果需要调用工具，按照格式输出工具调用；如果需要多步操作，每次只输出一步
3. 观察：获取工具执行结果
4. 反思：检查是否需要继续调用工具或可以总结回答
5. 总结：根据所有工具结果用自然语言回答用户

工具调用格式（选择一种）：
- 格式1：工具调用: tool_name(参数)
- 格式2：行动: tool_name 行动输入: 参数
- 格式3：Action: tool_name Action Input: 参数

完成标记：如果任务已完成不需要再调用工具，请输出【完成】后直接回答用户。

历史对话：
{chat_history}

之前的工具执行结果：
{tool_results}

用户问题：{user_input}

请输出你的思考、工具调用或最终回答：
"""
    return prompt.strip()


def build_summary_prompt(user_input, tool_calls, tool_results):
    """构建总结提示词"""
    calls_str = "\n".join([f"{i+1}. {call}" for i, call in enumerate(tool_calls)])
    results_str = "\n".join([f"{i+1}. {result}" for i, result in enumerate(tool_results)])
    
    prompt = f"""
用户问题: {user_input}

已执行的工具调用：
{calls_str}

工具执行结果：
{results_str}

请根据以上信息，用自然、友好、详细的语言总结回答用户的问题。
"""
    return prompt.strip()


def main():
    """主函数 - 启动 Agent 交互界面"""
    print("=" * 60)
    print("          AI Agent 交互界面")
    print("=" * 60)
    print("支持的功能:")
    print("  1. 计算器 - 执行数学运算")
    print("  2. 时间查询 - 获取当前时间")
    print("  3. 文件读取 - 读取本地文本文件")
    print("  4. 文件写入 - 创建或修改文本文件")
    print("  5. 文件删除 - 删除本地文件")
    print("  6. 对话记忆 - 记住历史对话")
    print("=" * 60)
    print("输入 'exit' 或 'quit' 退出程序")
    print("=" * 60)

    try:
        llm = create_agent()
        log_info("AI Agent 启动成功")
        
        # 加载插件和工具
        tool_count = load_plugins_and_tools()
        print(f"已加载 {tool_count} 个工具")
        log_info(f"已加载 {tool_count} 个工具")
        
        # 加载对话历史
        chat_history = load_chat_history()
        if chat_history:
            print(f"已加载 {len(chat_history)} 条历史对话")
            log_info(f"已加载 {len(chat_history)} 条历史对话")
        
        while True:
            user_input = input("\n请输入您的问题: ")
            
            if user_input.lower() in ["exit", "quit", "退出", "结束"]:
                # 保存对话历史
                save_chat_history(chat_history)
                print(f"已保存 {len(chat_history)} 条对话记录")
                log_info(f"已保存 {len(chat_history)} 条对话记录")
                print("感谢使用 AI Agent，再见！")
                log_info("AI Agent 退出")
                break
            
            if not user_input.strip():
                print("请输入有效的问题")
                continue
            
            # 安全检查
            security_result = validate_user_input(user_input)
            if not security_result["is_safe"]:
                error_msg = "输入安全检查失败:\n" + "\n".join(f"- {error}" for error in security_result["errors"])
                print(f"\n❌ {error_msg}")
                log_error(f"安全检查失败: {security_result['errors']}")
                continue
            
            # 记录安全警告
            if security_result["warnings"]:
                for warning in security_result["warnings"]:
                    log_info(f"安全警告: {warning}")
            
            # 清理输入
            user_input = sanitize_user_input(user_input)
            
            # 记录用户输入
            log_user_input(user_input)
            
            try:
                # 构建历史对话字符串
                history_str = "\n".join([f"用户: {h['user']}\n助手: {h['assistant']}" for h in chat_history])
                
                # 多轮推理循环（使用配置值）
                max_iterations = MAX_ITERATIONS
                iteration = 0
                tool_calls = []
                tool_results = []
                current_tool_results = ""
                final_response = None
                
                while iteration < max_iterations:
                    iteration += 1
                    
                    # 构建提示词，让 LLM 决定是否调用工具
                    prompt = build_agent_prompt(user_input, history_str, current_tool_results)
                    
                    # 调用 LLM 获取响应
                    response = llm.invoke([HumanMessage(content=prompt)]).content
                    
                    # 检查是否完成
                    if "【完成】" in response:
                        final_response = response.replace("【完成】", "").strip()
                        break
                    
                    # 提取工具调用
                    tool_name, params_str = extract_tool_call(response)
                    
                    if tool_name and tool_name in TOOLS:
                        # 解析参数并调用工具
                        parameters = parse_tool_parameters(tool_name, params_str or "")
                        tool_result = call_tool(tool_name, parameters)
                        
                        # 记录工具调用日志
                        log_tool_call(tool_name, params_str or "", tool_result)
                        
                        # 记录工具调用和结果
                        tool_calls.append(f"{tool_name}({params_str})")
                        tool_results.append(tool_result)
                        current_tool_results = "\n".join([f"{i+1}. {r}" for i, r in enumerate(tool_results)])
                        
                        # 显示中间步骤
                        print(f"\n[步骤 {iteration}] 工具调用: {tool_name}({params_str})")
                        print(f"[步骤 {iteration}] 执行结果: {tool_result}")
                    else:
                        # 没有工具调用，直接使用 LLM 的响应作为最终回答
                        final_response = response
                        break
                
                # 如果达到最大轮数仍未完成，进行总结
                if final_response is None and tool_calls:
                    summary_prompt = build_summary_prompt(user_input, tool_calls, tool_results)
                    final_response = llm.invoke([HumanMessage(content=summary_prompt)]).content
                
                # 如果仍然没有最终响应，使用最后一次 LLM 响应
                if final_response is None:
                    final_response = response
                
                # 记录响应日志
                log_response(final_response)
                
                # 显示回答
                print("\n" + "=" * 60)
                print(" Agent 回答: ")
                print()
                print(final_response)
                print("=" * 60)
                
                # 更新对话历史
                chat_history.append({
                    "user": user_input,
                    "assistant": final_response
                })
                
                # 限制历史记录长度（使用配置值）
                if len(chat_history) > HISTORY_LENGTH:
                    chat_history = chat_history[-HISTORY_LENGTH:]
            
            except Exception as e:
                print(f"\n发生错误: {str(e)}")
                print("请重试或输入其他问题")
        
    except Exception as e:
        print(f"Agent 初始化失败: {str(e)}")


if __name__ == "__main__":
    main()
