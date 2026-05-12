TOOL_NAME = "filter_by_preference"
DISPLAY_NAME = "Filter By Preference"
SCHEMA = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": "Re-rank existing design candidates according to user preference such as volume, loss, or compactness.",
        "parameters": {
            "type": "object",
            "properties": {
                "thinking": {"type": "string", "description": "Brief reasoning for why this tool is being called now."},
                "preference": {
                    "type": "string",
                    "enum": ["体积", "损耗", "紧凑", "volume", "loss", "compact", "default"],
                    "description": "Preference type."
                },
                "strength": {
                    "type": "string",
                    "enum": ["light", "medium", "strong"],
                    "description": "Preference strength.",
                    "default": "medium"
                }
            },
            "required": ["thinking", "preference"]
        },
    },
}
