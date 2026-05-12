import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {'1', 'true', 'yes', 'on'}


@dataclass(frozen=True)
class Settings:
    api_host: str = os.getenv('ANN_API_HOST', '0.0.0.0')
    api_port: int = int(os.getenv('ANN_API_PORT', '8000'))
    api_key: str = os.getenv('ANN_API_KEY', '')
    model_path: str = os.getenv('ANN_MODEL_PATH', '')
    device: str = os.getenv('ANN_DEVICE', 'cpu')
    runtime_mode: str = os.getenv('ANN_RUNTIME_MODE', 'checkpoint').strip().lower()
    max_points: int = int(os.getenv('ANN_MAX_POINTS', '50000'))
    default_batch_size: int = int(os.getenv('ANN_DEFAULT_BATCH_SIZE', '5000'))
    optimization_cache_size: int = int(os.getenv('ANN_OPTIMIZATION_CACHE_SIZE', '3'))
    allow_mock_model: bool = _get_bool('ANN_ALLOW_MOCK_MODEL', False)


settings = Settings()
