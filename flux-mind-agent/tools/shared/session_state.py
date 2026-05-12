from __future__ import annotations

DESIGN_PARAMETERS = {"ht", "c", "dc1", "dc2", "lg1", "Nx", "Ny"}
OPERATING_PARAMETERS = {"f", "i"}
TARGET_PARAMETERS = {"L", "P"}
ALLOWED_PARAMETERS = DESIGN_PARAMETERS | OPERATING_PARAMETERS | TARGET_PARAMETERS


def record_parameters(session: dict, parameter_dict: dict) -> bool:
    if not session or not isinstance(parameter_dict, dict) or not parameter_dict:
        return False
    if not all(key in ALLOWED_PARAMETERS for key in parameter_dict.keys()):
        return False
    for key, value in parameter_dict.items():
        session.setdefault("recorded_parameters", {})[key] = value
    return True


def get_recorded_parameters(session: dict) -> dict:
    if not session:
        return {}
    return session.get("recorded_parameters", {}).copy()


def get_missing_parameters(session: dict) -> list[str]:
    if not session:
        return list(ALLOWED_PARAMETERS)
    recorded = session.get("recorded_parameters", {})
    return [param for param in ALLOWED_PARAMETERS if param not in recorded]


def count_parameters_by_group(session: dict) -> dict[str, int]:
    recorded = get_recorded_parameters(session)
    keys = set(recorded.keys())
    return {
        "design": len(keys & DESIGN_PARAMETERS),
        "operating": len(keys & OPERATING_PARAMETERS),
        "target": len(keys & TARGET_PARAMETERS),
    }


def can_run_optimization(session: dict) -> bool:
    counts = count_parameters_by_group(session)
    return counts["design"] > 3 or counts["target"] >= 1
