#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent API Server - 使用 FastAPI 提供 RESTful API
"""

import os
import sys
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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
    log_info,
    log_error,
    log_user_input,
    log_response,
    log_tool_call,
    build_agent_prompt,
    build_summary_prompt,
    extract_tool_call,
    parse_tool_parameters,
    call_tool,
    MAX_ITERATIONS,
    HISTORY_LENGTH
)

from langchain_core.messages import HumanMessage

# 初始化 FastAPI
app = FastAPI(
    title="AI Agent API",
    description="AI Agent 的 RESTful API 接口",
    version="1.0.0"
)

# 全局变量
llm = None
chat_history = []

# 请求模型
class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    session_id: Optional[str] = None
    tool_used: bool = False
    tool_info: Optional[Dict[str, Any]] = None

class HistoryResponse(BaseModel):
    """历史记录响应模型"""
    summary: str
    count: int

class ConfigResponse(BaseModel):
    """配置响应模型"""
    success: bool
    message: str

# 启动时初始化
@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    global llm, chat_history
    try:
        llm = create_agent()
        chat_history = load_chat_history()
        log_info("API Server 启动成功")
        print("✅ API Server 启动成功")
    except Exception as e:
        log_error(f"API Server 启动失败: {str(e)}")
        print(f"❌ API Server 启动失败: {str(e)}")

# 关闭时清理
@app.on_event("shutdown")
async def shutdown_event():
    """关闭时保存历史"""
    global chat_history
    try:
        save_chat_history(chat_history)
        log_info("API Server 关闭，已保存对话历史")
    except Exception as e:
        log_error(f"保存对话历史失败: {str(e)}")

# 健康检查
@app.get("/health", summary="健康检查")
async def health_check():
    """检查 API 服务状态"""
    return {"status": "healthy", "service": "AI Agent API"}

# 聊天接口
@app.post("/chat", summary="发送消息", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """发送消息给 AI Agent"""
    global llm, chat_history
    
    if llm is None:
        raise HTTPException(status_code=500, detail="Agent 未初始化")
    
    user_input = request.message
    
    # 安全检查
    security_result = validate_user_input(user_input)
    if not security_result["is_safe"]:
        raise HTTPException(
            status_code=400,
            detail=f"安全检查失败: {', '.join(security_result['errors'])}"
        )
    
    # 清理输入
    user_input = sanitize_user_input(user_input)
    
    # 记录用户输入
    log_user_input(user_input)
    
    try:
        # 构建历史对话字符串
        history_str = "\n".join([f"用户: {h['user']}\n助手: {h['assistant']}" for h in chat_history])
        
        # 多轮推理循环
        max_iterations = MAX_ITERATIONS
        iteration = 0
        tool_calls = []
        tool_results = []
        current_tool_results = ""
        final_response = None
        tool_used = False
        
        while iteration < max_iterations:
            iteration += 1
            
            # 构建提示词
            prompt = build_agent_prompt(user_input, history_str, current_tool_results)
            
            # 调用 LLM
            response = llm.invoke([HumanMessage(content=prompt)]).content
            
            # 检查是否完成
            if "【完成】" in response:
                final_response = response.replace("【完成】", "").strip()
                break
            
            # 提取工具调用
            tool_name, params_str = extract_tool_call(response)
            
            if tool_name and tool_name in ["get_current_time", "calculate", "read_file", 
                                          "write_file", "delete_file", "web_search"]:
                # 解析参数并调用工具
                parameters = parse_tool_parameters(tool_name, params_str or "")
                tool_result = call_tool(tool_name, parameters)
                
                # 记录工具调用日志
                log_tool_call(tool_name, params_str or "", tool_result)
                
                # 记录工具调用和结果
                tool_calls.append(f"{tool_name}({params_str})")
                tool_results.append(tool_result)
                current_tool_results = "\n".join([f"{i+1}. {r}" for i, r in enumerate(tool_results)])
                tool_used = True
            else:
                # 没有工具调用，直接使用响应
                final_response = response
                break
        
        # 如果达到最大轮数仍未完成，进行总结
        if final_response is None and tool_calls:
            summary_prompt = build_summary_prompt(user_input, tool_calls, tool_results)
            final_response = llm.invoke([HumanMessage(content=summary_prompt)]).content
        
        # 如果仍然没有响应，使用最后一次响应
        if final_response is None:
            final_response = response
        
        # 记录响应日志
        log_response(final_response)
        
        # 更新对话历史
        chat_history.append({
            "user": user_input,
            "assistant": final_response
        })
        
        # 限制历史记录长度
        if len(chat_history) > HISTORY_LENGTH:
            chat_history = chat_history[-HISTORY_LENGTH:]
        
        return ChatResponse(
            response=final_response,
            session_id=request.session_id,
            tool_used=tool_used,
            tool_info={"calls": tool_calls, "results": tool_results} if tool_used else None
        )
    
    except Exception as e:
        log_error(f"聊天处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

# 获取历史摘要
@app.get("/history/summary", summary="获取历史摘要", response_model=HistoryResponse)
async def get_history():
    """获取对话历史摘要"""
    global chat_history
    summary = get_history_summary()
    return HistoryResponse(summary=summary, count=len(chat_history))

# 清空历史
@app.delete("/history", summary="清空历史", response_model=ConfigResponse)
async def clear_history():
    """清空所有对话历史"""
    global chat_history
    chat_history = []
    result = clear_chat_history()
    log_info("API: 清空对话历史")
    return ConfigResponse(success=True, message=result)

# 保存历史
@app.post("/history/save", summary="保存历史", response_model=ConfigResponse)
async def save_history():
    """保存对话历史到文件"""
    global chat_history
    try:
        save_chat_history(chat_history)
        log_info("API: 保存对话历史")
        return ConfigResponse(success=True, message="对话历史已保存")
    except Exception as e:
        return ConfigResponse(success=False, message=f"保存失败: {str(e)}")

# 获取工具列表
@app.get("/tools", summary="获取可用工具列表")
async def get_tools():
    """获取所有可用工具"""
    tools = [
        {"name": "get_current_time", "description": "获取当前时间", "parameters": []},
        {"name": "calculate", "description": "执行数学运算", "parameters": ["expression"]},
        {"name": "read_file", "description": "读取文件", "parameters": ["file_path"]},
        {"name": "write_file", "description": "写入文件", "parameters": ["file_path", "content"]},
        {"name": "delete_file", "description": "删除文件", "parameters": ["file_path"]},
        {"name": "web_search", "description": "网络搜索", "parameters": ["query"]},
        {"name": "get_history_summary", "description": "获取历史摘要", "parameters": []},
        {"name": "clear_chat_history", "description": "清空历史", "parameters": []}
    ]
    return {"tools": tools}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")