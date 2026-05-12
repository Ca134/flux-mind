TOOL_NAME = "record_params"
DISPLAY_NAME = "Record Params"
SCHEMA = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": 'Record user-provided parameters. Supported keys: ht, c, dc1, dc2, lg1, Nx, Ny, f, i, L, P. Supports exact values and ranges. Use engineering units: geometry in mm, f in kHz, i in A, L in uH, P in W. Example: f=200, L={"min":5,"max":10}, i={"min":2,"max":5}, P={"min":1,"max":3}.',
        "parameters": {
            "type": "object",
            "properties": {
                "thinking": {"type": "string", "description": "Brief reasoning for why this tool is being called now."},
                "params": {
                    "type": "object",
                    "description": 'Parameter dictionary, for example {"ht": 10}, {"lg1": 1.1}, or {"ht": {"min": 5, "max": 15}}.'
                }
            },
            "required": ["thinking", "params"]
        },
    },
}
