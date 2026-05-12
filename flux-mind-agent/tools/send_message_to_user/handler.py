from __future__ import annotations

from tools.context import ToolContext, ToolResult


def handle(context: ToolContext, arguments: dict) -> ToolResult:
    msg_content = arguments.get("message", "")
    message_id = f"stream_{context.socket_id}_{context.session['round_num']}"
    context.emit_stream_message(context.socket_id, message_id, msg_content)
    context.session["status"] = "waiting"
    return ToolResult(return_value="This tool has no return value")
