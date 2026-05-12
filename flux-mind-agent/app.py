from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from openai import OpenAI
from dotenv import load_dotenv
import json
import numpy as np
import pandas as pd
import sys
import os

from core.prompt_runtime import BASE_PROMPT as base_prompt
from core.session import cleanup_session, create_session, get_session, input_events, reset_session
from tools.shared.experiment_logger import exp_logger
from tools import TOOLS_DEFINITION, TOOL_NAME_MAP, execute_tool
from tools.context import ToolContext
from tools.shared.session_state import get_recorded_parameters


load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# 在当前 Windows + torch 环境中，gevent 的线程 monkey patch
# 会与调试重载/退出流程冲突，因此固定使用 threading 模式。
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    ping_timeout=300,      # 5分钟超时
    ping_interval=25,      # 25秒心跳间隔
    async_mode="threading"
)

# OpenAI 客户端配置
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
SILICONFLOW_BASE_URL = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")

if not SILICONFLOW_API_KEY:
    raise RuntimeError("SILICONFLOW_API_KEY is required. Set it in the environment or .env file.")

client = OpenAI(
    api_key=SILICONFLOW_API_KEY,
    base_url=SILICONFLOW_BASE_URL
)

MAX_HISTORY_MESSAGES = 20

# 存储连接的客户端 socket IDs
connected_clients = {}

def update_system_logs(socket_id, tool, parameter, purpose, return_value):
    """更新系统日志"""
    session = get_session(socket_id)
    if not session:
        return
    
    log_entry = {
        "tool": tool,
        "parameter": parameter,
        "purpose": purpose,
        "return_value": return_value
    }
    session["system_logs"].append(log_entry)
    if len(session["system_logs"]) > 10:
        session["system_logs"].pop(0)

def add_user_interaction(socket_id, msg_type, content):
    """添加用户交互记录"""
    session = get_session(socket_id)
    if not session:
        return
    
    session["user_interaction_history"].append({
        "type": msg_type,
        "content": content
    })
    while len(session["user_interaction_history"]) > 8:
        session["user_interaction_history"].pop(0)

def stringify_return_value(value):
    """将工具返回值统一转换为可回填到 tool message 的字符串"""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)

def build_assistant_message_dict(message):
    """兼容 OpenAI SDK 对象，保留 assistant/tool_calls 原始结构"""
    if hasattr(message, "model_dump"):
        return message.model_dump(exclude_none=True)
    return {
        "role": "assistant",
        "content": getattr(message, "content", None),
        "tool_calls": getattr(message, "tool_calls", None),
    }

def print_model_response(socket_id, round_num, message):
    """打印模型原始响应，便于调试 tool calling 行为"""
    print(f"\n{'='*80}", flush=True)
    print(f"Socket {socket_id} - 第 {round_num} 轮 - 模型原始响应:", flush=True)
    print(f"{'='*80}", flush=True)
    if hasattr(message, "model_dump"):
        print(json.dumps(message.model_dump(exclude_none=True), ensure_ascii=False, indent=2, default=str), flush=True)
    else:
        print(json.dumps(build_assistant_message_dict(message), ensure_ascii=False, indent=2, default=str), flush=True)
    print(f"{'='*80}\n", flush=True)

def emit_stream_message(socket_id, message_id, message_content, chunk_size=24, delay_seconds=0.005):
    """以分块方式流式发送消息，避免阻塞 SocketIO 事件循环"""
    text = str(message_content or "")
    if not text:
        socketio.emit('ai_message_stream', {
            'content': '',
            'message_id': message_id,
            'is_complete': True
        }, room=socket_id)
        return

    for start in range(0, len(text), chunk_size):
        socketio.emit('ai_message_stream', {
            'content': text[start:start + chunk_size],
            'message_id': message_id,
            'is_complete': False
        }, room=socket_id)
        socketio.sleep(delay_seconds)

    socketio.emit('ai_message_stream', {
        'content': '',
        'message_id': message_id,
        'is_complete': True
    }, room=socket_id)

def trim_message_history(messages, max_history_messages=MAX_HISTORY_MESSAGES):
    """保留 system prompt 与最近若干条非 system messages"""
    if not messages:
        return messages

    system_messages = [message for message in messages if message.get("role") == "system"]
    non_system_messages = [message for message in messages if message.get("role") != "system"]

    trimmed_messages = non_system_messages[-max_history_messages:]
    messages[:] = system_messages[:1] + trimmed_messages
    return messages

@app.route('/api/start-session', methods=['POST'])
def start_session():
    """此路由已弃用，使用 WebSocket 事件代替"""
    return jsonify({"status": "use websocket instead"})

@app.route('/api/get-status', methods=['GET'])
def get_status():
    """获取当前会话状态（此路由已弃用，使用 WebSocket 事件代替）"""
    return jsonify({"status": "use websocket instead"})

def send_to_frontend(socket_id, message_type, content):
    """向前端发送消息"""
    socketio.emit(message_type, {"content": content}, room=socket_id)

# WebSocket 事件处理
@socketio.on('connect')
def handle_connect():
    """客户端连接时"""
    print(f"客户端连接: {request.sid}")
    connected_clients[request.sid] = request.sid
    create_session(request.sid, base_prompt)

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    socket_id = request.sid
    if socket_id in connected_clients:
        del connected_clients[socket_id]
    cleanup_session(socket_id)
    print(f"客户端断开连接: {socket_id}")

@socketio.on('start_session')
def handle_start_session():
    """启动会话"""
    socket_id = request.sid
    session = reset_session(socket_id, base_prompt)
    session["status"] = "processing"
    
    print(f"会话已启动，socket_id: {socket_id}", flush=True)
    socketio.start_background_task(run_dialog_loop, socket_id)
    
    return {"status": "started"}

@socketio.on('user_input')
def handle_user_input(data):
    """接收用户输入"""
    socket_id = request.sid
    session = get_session(socket_id)
    if session:
        user_input = data.get('message', '')
        session["pending_input"]["user_input"] = user_input
        if socket_id in input_events:
            input_events[socket_id].set()

@socketio.on('return_value')
def handle_return_value(data):
    """接收 return_value"""
    socket_id = request.sid
    session = get_session(socket_id)
    if session:
        return_value = data.get('return_value', '')
        session["pending_input"]["return_value"] = return_value
        if socket_id in input_events:
            input_events[socket_id].set()

def run_dialog_loop(socket_id):
    """运行对话循环（使用原生工具调用）"""
    session = get_session(socket_id)
    if not session:
        return

    exp_logger.init_session(socket_id)
    messages = session["messages"]
    optimization_triggered = False
    optimization_success = False
    consecutive_errors = 0  # 连续错误计数
    MAX_CONSECUTIVE_ERRORS = 3  # 最大连续错误次数

    while session["round_num"] <= session["max_rounds"]:
        # 检查 socket 是否仍然连接
        if socket_id not in connected_clients:
            print(f"Socket {socket_id} 已断开，终止对话循环")
            break

        session["status"] = "processing"
        exp_logger.increment("total_rounds")

        # 打印发送给 LLM 的消息
        print(f"\n{'='*80}", flush=True)
        print(f"Socket {socket_id} - 第 {session['round_num']} 轮 - 发送给 LLM 的 Messages:", flush=True)
        print(f"{'='*80}", flush=True)
        print(json.dumps(messages, ensure_ascii=False, indent=2, default=str), flush=True)
        print(f"{'='*80}\n", flush=True)

        try:
            # 调用 LLM
            response = client.chat.completions.create(
                model="Pro/zai-org/GLM-5",
                messages=messages,
                tools=TOOLS_DEFINITION,
                temperature=0.3,
                top_p=0.7,
                stream=False,
                extra_body={"enable_thinking": False}
            )

            if not getattr(response, "choices", None):
                consecutive_errors += 1
                print(f"警告: 模型返回空 choices，连续错误 {consecutive_errors}/{MAX_CONSECUTIVE_ERRORS}")
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    send_to_frontend(socket_id, "error", "模型响应为空，会话终止")
                    break
                session["round_num"] += 1
                continue

            message = response.choices[0].message
            print_model_response(socket_id, session["round_num"], message)
            messages.append(build_assistant_message_dict(message))

            # 检查是否有工具调用
            if getattr(message, "tool_calls", None):
                consecutive_errors = 0
                should_terminate = False

                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_name_cn = TOOL_NAME_MAP.get(tool_name, tool_name)

                    # 解析工具参数
                    try:
                        arguments = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                    except json.JSONDecodeError:
                        arguments = {}

                    print(f"工具调用: {tool_name}, 参数: {arguments}")

                    # 埋点：工具解析成功
                    exp_logger.log_tool_parse(
                        success=True,
                        round_number=session["round_num"],
                        raw_output=f"tool_call: {tool_name}({arguments})",
                        parsed_tool=tool_name_cn,
                        parsed_params=arguments
                    )

                    return_value_input = None
                    purpose = f"call {tool_name}"
                    tool_context = ToolContext(
                        socket_id=socket_id,
                        session=session,
                        input_events=input_events,
                        send_to_frontend=send_to_frontend,
                        emit_stream_message=emit_stream_message,
                        add_user_interaction=add_user_interaction,
                        exp_logger=exp_logger,
                    )
                    tool_result = execute_tool(tool_name, arguments, tool_context)
                    return_value_input = tool_result.return_value
                    if tool_result.purpose:
                        purpose = tool_result.purpose
                    if tool_name == "run_optimization":
                        optimization_triggered = optimization_triggered or session.get("optimization_triggered", False)
                        optimization_success = optimization_success or session.get("optimization_success", False)
                    if tool_result.should_terminate:
                        should_terminate = True
                        break

                    tool_result_content = stringify_return_value(return_value_input)

                    try:
                        return_value = json.loads(tool_result_content) if tool_result_content else None
                    except (json.JSONDecodeError, TypeError):
                        return_value = return_value_input

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result_content,
                    })

                    update_system_logs(socket_id, tool_name_cn, arguments, purpose, return_value)

                trim_message_history(messages)

                if should_terminate:
                    break

            else:
                consecutive_errors += 1
                assistant_text = message.content or ""
                print(f"警告: 模型未调用工具，连续错误 {consecutive_errors}/{MAX_CONSECUTIVE_ERRORS}")
                exp_logger.log_tool_parse(
                    success=False,
                    round_number=session["round_num"],
                    raw_output=assistant_text,
                    error_message="No tool call in response"
                )

                if assistant_text:
                    print("警告: 模型直接输出了 assistant 文本；已追加系统纠正提示，要求后续通过 tool 与用户交互")
                    messages.append({
                        "role": "system",
                        "content": "你刚刚直接输出了 assistant 文本，这是不允许的。请不要直接回复用户；所有面向用户的内容必须通过 send_message_to_user，所有需要用户继续输入的场景必须通过 receive_user_input。请立即改用工具继续。"
                    })

                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    send_to_frontend(socket_id, "error", "模型响应异常，会话终止")
                    break

        except Exception as e:
            consecutive_errors += 1
            error_msg = str(e)
            print(f"错误: {error_msg}，连续错误 {consecutive_errors}/{MAX_CONSECUTIVE_ERRORS}")
            send_to_frontend(socket_id, "error", f"调用模型出错: {error_msg}")

            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                print(f"连续错误达到上限，终止会话")
                break

        session["round_num"] += 1

    # 埋点：会话结束摘要
    exp_logger.log_session_summary(
        final_params=get_recorded_parameters(session),
        optimization_triggered=optimization_triggered,
        optimization_success=optimization_success
    )
    send_to_frontend(socket_id, "session_end", "对话已结束")

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
    )



