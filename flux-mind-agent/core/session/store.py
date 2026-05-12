from __future__ import annotations

from typing import Any
import threading


sessions: dict[str, dict[str, Any]] = {}
input_events: dict[str, threading.Event] = {}


def build_session_payload(socket_id: str, system_prompt: str) -> dict[str, Any]:
    return {
        "round_num": 1,
        "max_rounds": 999999,
        "status": "waiting",
        "system_logs": [],
        "user_interaction_history": [],
        "messages": [{"role": "system", "content": system_prompt}],
        "recorded_parameters": {},
        "pending_input": {"user_input": None, "return_value": None},
        "current_socket_id": socket_id,
        "active_profiles": [],
        "slots": {},
        "transition_log": [],
    }


def create_session(socket_id: str, system_prompt: str) -> dict[str, Any]:
    session = build_session_payload(socket_id, system_prompt)
    sessions[socket_id] = session
    input_events[socket_id] = threading.Event()
    return session


def get_session(socket_id: str) -> dict[str, Any]:
    return sessions.get(socket_id, {})


def reset_session(socket_id: str, system_prompt: str) -> dict[str, Any]:
    session = build_session_payload(socket_id, system_prompt)
    sessions[socket_id] = session
    input_events.setdefault(socket_id, threading.Event()).clear()
    return session


def cleanup_session(socket_id: str) -> None:
    if socket_id in sessions:
        del sessions[socket_id]
    if socket_id in input_events:
        del input_events[socket_id]
