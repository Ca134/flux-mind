from __future__ import annotations

from tools.context import ToolContext, ToolResult

WAITING_MESSAGE = "等待用户输入..."
TIMEOUT_MESSAGE = "等待输入超时"
USER_MESSAGE_LABEL = "用户消息"


def handle(context: ToolContext, arguments: dict) -> ToolResult:
    context.send_to_frontend(context.socket_id, "request_user_input", WAITING_MESSAGE)
    context.session["status"] = "waiting_input"
    context.session["pending_input"]["user_input"] = None

    event = context.input_events[context.socket_id]
    event.clear()
    if not event.wait(timeout=300):
        print(f"Socket {context.socket_id} {TIMEOUT_MESSAGE}")
        context.send_to_frontend(context.socket_id, "error", TIMEOUT_MESSAGE)
        return ToolResult(return_value=TIMEOUT_MESSAGE, should_terminate=True)

    value = context.session["pending_input"]["user_input"]
    context.add_user_interaction(context.socket_id, USER_MESSAGE_LABEL, value)
    return ToolResult(return_value=value)
