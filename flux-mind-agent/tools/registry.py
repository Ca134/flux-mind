from __future__ import annotations

from tools.context import ToolContext, ToolResult

from .get_missing_params import DISPLAY_NAME as GET_MISSING_PARAMS_LABEL, SCHEMA as GET_MISSING_PARAMS_SCHEMA, TOOL_NAME as GET_MISSING_PARAMS_NAME, handle as handle_get_missing_params
from .send_message_to_user import DISPLAY_NAME as SEND_MESSAGE_TO_USER_LABEL, SCHEMA as SEND_MESSAGE_TO_USER_SCHEMA, TOOL_NAME as SEND_MESSAGE_TO_USER_NAME, handle as handle_send_message_to_user
from .receive_user_input import DISPLAY_NAME as RECEIVE_USER_INPUT_LABEL, SCHEMA as RECEIVE_USER_INPUT_SCHEMA, TOOL_NAME as RECEIVE_USER_INPUT_NAME, handle as handle_receive_user_input
from .query_knowledge_base import DISPLAY_NAME as QUERY_KNOWLEDGE_BASE_LABEL, SCHEMA as QUERY_KNOWLEDGE_BASE_SCHEMA, TOOL_NAME as QUERY_KNOWLEDGE_BASE_NAME, handle as handle_query_knowledge_base
from .get_param_importance import DISPLAY_NAME as GET_PARAM_IMPORTANCE_LABEL, SCHEMA as GET_PARAM_IMPORTANCE_SCHEMA, TOOL_NAME as GET_PARAM_IMPORTANCE_NAME, handle as handle_get_param_importance
from .run_optimization import DISPLAY_NAME as RUN_OPTIMIZATION_LABEL, SCHEMA as RUN_OPTIMIZATION_SCHEMA, TOOL_NAME as RUN_OPTIMIZATION_NAME, handle as handle_run_optimization
from .get_param_count import DISPLAY_NAME as GET_PARAM_COUNT_LABEL, SCHEMA as GET_PARAM_COUNT_SCHEMA, TOOL_NAME as GET_PARAM_COUNT_NAME, handle as handle_get_param_count
from .record_params import DISPLAY_NAME as RECORD_PARAMS_LABEL, SCHEMA as RECORD_PARAMS_SCHEMA, TOOL_NAME as RECORD_PARAMS_NAME, handle as handle_record_params
from .filter_by_preference import DISPLAY_NAME as FILTER_BY_PREFERENCE_LABEL, SCHEMA as FILTER_BY_PREFERENCE_SCHEMA, TOOL_NAME as FILTER_BY_PREFERENCE_NAME, handle as handle_filter_by_preference

TOOLS_DEFINITION = [
    GET_MISSING_PARAMS_SCHEMA,
    SEND_MESSAGE_TO_USER_SCHEMA,
    RECEIVE_USER_INPUT_SCHEMA,
    QUERY_KNOWLEDGE_BASE_SCHEMA,
    GET_PARAM_IMPORTANCE_SCHEMA,
    RUN_OPTIMIZATION_SCHEMA,
    GET_PARAM_COUNT_SCHEMA,
    RECORD_PARAMS_SCHEMA,
    FILTER_BY_PREFERENCE_SCHEMA,
]

TOOL_NAME_MAP = {
    GET_MISSING_PARAMS_NAME: GET_MISSING_PARAMS_LABEL,
    SEND_MESSAGE_TO_USER_NAME: SEND_MESSAGE_TO_USER_LABEL,
    RECEIVE_USER_INPUT_NAME: RECEIVE_USER_INPUT_LABEL,
    QUERY_KNOWLEDGE_BASE_NAME: QUERY_KNOWLEDGE_BASE_LABEL,
    GET_PARAM_IMPORTANCE_NAME: GET_PARAM_IMPORTANCE_LABEL,
    RUN_OPTIMIZATION_NAME: RUN_OPTIMIZATION_LABEL,
    GET_PARAM_COUNT_NAME: GET_PARAM_COUNT_LABEL,
    RECORD_PARAMS_NAME: RECORD_PARAMS_LABEL,
    FILTER_BY_PREFERENCE_NAME: FILTER_BY_PREFERENCE_LABEL,
}

_HANDLERS = {
    GET_MISSING_PARAMS_NAME: handle_get_missing_params,
    SEND_MESSAGE_TO_USER_NAME: handle_send_message_to_user,
    RECEIVE_USER_INPUT_NAME: handle_receive_user_input,
    QUERY_KNOWLEDGE_BASE_NAME: handle_query_knowledge_base,
    GET_PARAM_IMPORTANCE_NAME: handle_get_param_importance,
    RUN_OPTIMIZATION_NAME: handle_run_optimization,
    GET_PARAM_COUNT_NAME: handle_get_param_count,
    RECORD_PARAMS_NAME: handle_record_params,
    FILTER_BY_PREFERENCE_NAME: handle_filter_by_preference,
}


def execute_tool(tool_name: str, arguments: dict, context: ToolContext) -> ToolResult:
    if tool_name not in _HANDLERS:
        return ToolResult(return_value=f"Unknown tool: {tool_name}")
    return _HANDLERS[tool_name](context, arguments)
