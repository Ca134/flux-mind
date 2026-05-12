TOOL_NAME = "send_message_to_user"
DISPLAY_NAME = "Send Message To User"
SCHEMA = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": "Send a message to the user for explanation, confirmation, or guidance.",
        "parameters": {
            "type": "object",
            "properties": {
                "thinking": {"type": "string", "description": "Brief reasoning for why this tool is being called now."},
                "message": {"type": "string", "description": "Message content to display to the user."}
            },
            "required": ["thinking", "message"]
        },
    },
}
