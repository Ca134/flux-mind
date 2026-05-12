TOOL_NAME = "run_optimization"
DISPLAY_NAME = "Run Optimization"
SCHEMA = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": "Run design optimization based on currently recorded parameters.",
        "parameters": {"type": "object", "properties": {"thinking": {"type": "string", "description": "Brief reasoning for why this tool is being called now."}}, "required": ["thinking"]},
    },
}
