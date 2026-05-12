TOOL_NAME = "receive_user_input"
DISPLAY_NAME = "Receive User Input"
SCHEMA = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": "Wait for and receive the next user input.",
        "parameters": {"type": "object", "properties": {"thinking": {"type": "string", "description": "Brief reasoning for why this tool is being called now."}}, "required": ["thinking"]},
    },
}
