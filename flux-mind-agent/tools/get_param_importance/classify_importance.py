def classify_importance(text: str) -> str:
    if text in ["i", "f", "Nx", "Ny"]:
        return "High"
    elif text in ["ht", "dc1", "dc2"]:
        return "Middle"
    else:
        return "Low"