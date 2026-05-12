from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping
import threading


@dataclass
class ToolResult:
    return_value: Any
    purpose: str | None = None
    should_terminate: bool = False


@dataclass
class ToolContext:
    socket_id: str
    session: dict[str, Any]
    input_events: Mapping[str, threading.Event]
    send_to_frontend: Callable[[str, str, Any], None]
    emit_stream_message: Callable[[str, str, Any], None]
    add_user_interaction: Callable[[str, str, Any], None]
    exp_logger: Any
