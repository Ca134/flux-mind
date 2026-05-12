TOOL_NAME = "get_param_importance"
DISPLAY_NAME = "Get Param Importance"
SCHEMA = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": "Return the importance level and explanation for a design parameter.",
        "parameters": {
            "type": "object",
            "properties": {
                "thinking": {"type": "string", "description": "Brief reasoning for why this tool is being called now."},
                "param_name": {"type": "string", "description": "Parameter name, for example 'ht'."}
            },
            "required": ["thinking", "param_name"]
        },
    },
}
