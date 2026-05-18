#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent 图形化界面 - 使用 Streamlit
"""

import os
import sys
import json
import streamlit as st
from datetime import datetime
from io import StringIO

# 添加主模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (
    create_agent,
    load_chat_history,
    save_chat_history,
    clear_chat_history,
    get_history_summary,
    validate_user_input,
    sanitize_user_input,
    log_user_input,
    log_response,
    log_tool_call,
    build_agent_prompt,
    build_summary_prompt,
    extract_tool_call,
    parse_tool_parameters,
    call_tool,
    load_plugins_and_tools,
    TOOLS,
    MAX_ITERATIONS,
    HISTORY_LENGTH
)

from performance_monitor import get_all_performance_summaries

from langchain_core.messages import HumanMessage

# 页面配置
st.set_page_config(
    page_title="AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 全局变量
if "llm" not in st.session_state:
    st.session_state.llm = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "initialized" not in st.session_state:
    st.session_state.initialized = False

if "theme" not in st.session_state:
    st.session_state.theme = "light"  # light or dark

# 初始化函数
def initialize_agent():
    """初始化 Agent"""
    if st.session_state.initialized:
        return
    
    try:
        # 加载插件和工具
        load_plugins_and_tools()
        
        # 创建 LLM
        st.session_state.llm = create_agent()
        
        # 加载对话历史
        st.session_state.chat_history = load_chat_history()
        
        st.session_state.initialized = True
        st.success("AI Agent 初始化成功！")
    except Exception as e:
        st.error(f"初始化失败: {str(e)}")

# 聊天函数
def process_message(user_input):
    """处理用户消息"""
    if not st.session_state.llm:
        return "错误：Agent 未初始化"
    
    # 安全检查
    security_result = validate_user_input(user_input)
    if not security_result["is_safe"]:
        error_msg = "输入安全检查失败:\n" + "\n".join(f"- {error}" for error in security_result["errors"])
        return f"❌ {error_msg}"
    
    # 清理输入
    user_input = sanitize_user_input(user_input)
    
    # 记录用户输入
    log_user_input(user_input)
    
    try:
        # 构建历史对话字符串
        history_str = "\n".join([f"用户: {h['user']}\n助手: {h['assistant']}" for h in st.session_state.chat_history])
        
        # 多轮推理循环
        max_iterations = MAX_ITERATIONS
        iteration = 0
        tool_calls = []
        tool_results = []
        current_tool_results = ""
        final_response = None
        
        while iteration < max_iterations:
            iteration += 1
            
            # 构建提示词
            prompt = build_agent_prompt(user_input, history_str, current_tool_results)
            
            # 调用 LLM
            response = st.session_state.llm.invoke([HumanMessage(content=prompt)]).content
            
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
            else:
                # 没有工具调用，直接使用响应
                final_response = response
                break
        
        # 如果达到最大轮数仍未完成，进行总结
        if final_response is None and tool_calls:
            summary_prompt = build_summary_prompt(user_input, tool_calls, tool_results)
            final_response = st.session_state.llm.invoke([HumanMessage(content=summary_prompt)]).content
        
        # 如果仍然没有响应，使用最后一次响应
        if final_response is None:
            final_response = response
        
        # 记录响应日志
        log_response(final_response)
        
        # 更新对话历史
        st.session_state.chat_history.append({
            "user": user_input,
            "assistant": final_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史记录长度
        if len(st.session_state.chat_history) > HISTORY_LENGTH:
            st.session_state.chat_history = st.session_state.chat_history[-HISTORY_LENGTH:]
        
        return final_response
    
    except Exception as e:
        return f"错误：{str(e)}"

# 导出聊天历史
def export_chat_history(format_type="json"):
    """导出聊天历史"""
    if not st.session_state.chat_history:
        return None, None
    
    if format_type == "json":
        data = json.dumps(st.session_state.chat_history, ensure_ascii=False, indent=2)
        filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        mime_type = "application/json"
    elif format_type == "markdown":
        lines = ["# 聊天历史", ""]
        for i, message in enumerate(st.session_state.chat_history, 1):
            timestamp = message.get("timestamp", "")
            if timestamp:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                lines.append(f"---\n## 对话 {i} ({time_str})")
            else:
                lines.append(f"---\n## 对话 {i}")
            lines.append(f"**用户**: {message['user']}")
            lines.append(f"**助手**: {message['assistant']}")
            lines.append("")
        data = "\n".join(lines)
        filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        mime_type = "text/markdown"
    elif format_type == "txt":
        lines = []
        for i, message in enumerate(st.session_state.chat_history, 1):
            timestamp = message.get("timestamp", "")
            if timestamp:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                lines.append(f"=== 对话 {i} ({time_str}) ===")
            else:
                lines.append(f"=== 对话 {i} ===")
            lines.append(f"用户: {message['user']}")
            lines.append(f"助手: {message['assistant']}")
            lines.append("")
        data = "\n".join(lines)
        filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        mime_type = "text/plain"
    else:
        return None, None
    
    return data, filename

# 切换主题
def toggle_theme():
    """切换主题"""
    if st.session_state.theme == "light":
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"

# 主界面
def main():
    """主界面"""
    # 应用主题样式
    if st.session_state.theme == "dark":
        st.markdown("""
            <style>
            .stApp {
                background-color: #1a1a2e;
                color: #ffffff;
            }
            .stChatMessage {
                background-color: #16213e;
            }
            .stTextInput > div > div > input {
                background-color: #0f3460;
                color: #ffffff;
            }
            .stButton > button {
                background-color: #0f3460;
                color: #ffffff;
                border: 1px solid #4a69bd;
            }
            .stSidebar {
                background-color: #0f3460;
            }
            </style>
        """, unsafe_allow_html=True)
    
    # 标题区域
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🤖 AI Agent")
    with col2:
        # 主题切换按钮
        theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
        st.button(theme_icon, on_click=toggle_theme, key="theme_btn", help="切换主题")
    
    # 侧边栏
    with st.sidebar:
        st.header("控制面板")
        
        # 初始化按钮
        if st.button("初始化 Agent", key="init_btn"):
            initialize_agent()
        
        # 保存历史
        if st.button("保存对话历史", key="save_btn"):
            try:
                save_chat_history(st.session_state.chat_history)
                st.success("对话历史已保存")
            except Exception as e:
                st.error(f"保存失败: {str(e)}")
        
        # 导出历史
        st.subheader("导出对话")
        export_format = st.selectbox("选择格式", ["JSON", "Markdown", "纯文本"], key="export_format")
        
        if st.button("导出对话历史", key="export_btn"):
            format_map = {"JSON": "json", "Markdown": "markdown", "纯文本": "txt"}
            data, filename = export_chat_history(format_map[export_format])
            if data:
                st.download_button(
                    label=f"下载 {filename}",
                    data=data,
                    file_name=filename,
                    mime="text/plain"
                )
                st.success("准备下载...")
            else:
                st.warning("没有可导出的对话历史")
        
        # 清空历史
        if st.button("清空对话历史", key="clear_btn"):
            try:
                st.session_state.chat_history = []
                clear_chat_history()
                st.success("对话历史已清空")
            except Exception as e:
                st.error(f"清空失败: {str(e)}")
        
        # 工具列表
        st.header("可用工具")
        for tool_name, tool_info in TOOLS.items():
            with st.expander(tool_name):
                st.write(f"**描述**: {tool_info['description']}")
                st.write(f"**参数**: {', '.join(tool_info['parameters']) if tool_info['parameters'] else '无'}")
        
        # 性能监控
        st.header("性能监控")
        if st.button("刷新性能数据", key="refresh_perf"):
            perf_data = get_all_performance_summaries()
            if "global" in perf_data:
                global_perf = perf_data["global"]
                st.write(f"**总调用**: {global_perf['total_calls']}")
                st.write(f"**成功率**: {global_perf['success_rate']}")
                st.write(f"**平均响应时间**: {global_perf['avg_response_time']}")
                st.write(f"**P95响应时间**: {global_perf['p95_response_time']}")
    
    # 主聊天区域
    st.subheader("聊天窗口")
    
    # 显示聊天历史
    for i, message in enumerate(st.session_state.chat_history):
        # 用户消息
        with st.chat_message("user", avatar="👤"):
            st.write(message["user"])
            # 复制按钮
            if st.button(f"📋 复制", key=f"copy_user_{i}", help="复制消息"):
                st.session_state.chat_history[i]["copied"] = True
                st.toast("已复制到剪贴板")
        
        # 助手消息
        with st.chat_message("assistant", avatar="🤖"):
            st.write(message["assistant"])
            # 复制按钮
            if st.button(f"📋 复制", key=f"copy_assistant_{i}", help="复制消息"):
                st.session_state.chat_history[i]["copied"] = True
                st.toast("已复制到剪贴板")
    
    # 用户输入
    user_input = st.chat_input("请输入您的问题...")
    
    if user_input:
        # 检查是否已初始化
        if not st.session_state.initialized:
            st.warning("请先点击左侧的 '初始化 Agent' 按钮")
            return
        
        # 显示用户消息
        with st.chat_message("user", avatar="👤"):
            st.write(user_input)
        
        # 处理消息
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("正在思考..."):
                response = process_message(user_input)
            st.write(response)

if __name__ == "__main__":
    main()
