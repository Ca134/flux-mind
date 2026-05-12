TOOL_NAME = "get_param_count"
DISPLAY_NAME = "Get Param Count"
SCHEMA = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": "Return grouped parameter counts as a JSON object with total, design, operating, and target fields. Use the target count to determine whether L/P has already been provided.",
        "parameters": {"type": "object", "properties": {"thinking": {"type": "string", "description": "Brief reasoning for why this tool is being called now."}}, "required": ["thinking"]},
    },
}
