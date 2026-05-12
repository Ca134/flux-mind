TOOL_NAME = "get_missing_params"
DISPLAY_NAME = "Get Missing Params"
SCHEMA = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": "Return the list of parameters that have not been recorded yet.",
        "parameters": {"type": "object", "properties": {"thinking": {"type": "string", "description": "Brief reasoning for why this tool is being called now."}}, "required": ["thinking"]},
    },
}
