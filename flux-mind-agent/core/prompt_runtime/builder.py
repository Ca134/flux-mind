from __future__ import annotations

from typing import Any, Mapping
import json


def format_system_logs(session: Mapping[str, Any]) -> str:
    if not session or not session.get("system_logs"):
        return "**系统日志：当前无记录**"

    logs_str = "系统日志：\n"
    for index, log in enumerate(session["system_logs"], 1):
        logs_str += json.dumps(log, ensure_ascii=False, indent=2)
        if index < len(session["system_logs"]):
            logs_str += ",\n"
    return logs_str


def format_last_round_info(session: Mapping[str, Any]) -> str:
    if not session or not session.get("system_logs"):
        return "**上一轮调用的工具及返回：none, 当前为第一轮**"

    last_log = session["system_logs"][-1]
    return f"""上一轮调用的工具及返回：{json.dumps(last_log, ensure_ascii=False)}"""


def format_user_interaction_history(session: Mapping[str, Any]) -> str:
    if not session or not session.get("user_interaction_history"):
        return "**用户交互记录：暂无交互**"

    history_str = "**用户交互记录：**\n"
    for interaction in session["user_interaction_history"][-4:]:
        history_str += str(interaction["type"]) + ": " + str(interaction["content"]) + "\n"
    return history_str


def build_prompt_with_context(session: Mapping[str, Any], base_prompt: str) -> str:
    return f"""{base_prompt}

{format_system_logs(session)}

{format_last_round_info(session)}
"""
