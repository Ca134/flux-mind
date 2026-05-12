TOOL_NAME = "query_knowledge_base"
DISPLAY_NAME = "Query Knowledge Base"
SCHEMA = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": "Query the backend knowledge base for technical definitions or guidance.",
        "parameters": {
            "type": "object",
            "properties": {
                "thinking": {"type": "string", "description": "Brief reasoning for why this tool is being called now."},
                "query": {"type": "string", "description": "Query text, for example 'What does ht mean in inductor design?'"}
            },
            "required": ["thinking", "query"]
        },
    },
}
