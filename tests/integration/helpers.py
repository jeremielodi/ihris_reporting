import json
from pathlib import Path

MOCK_DIR = Path(__file__).parent /".."/ "mock"


def load_mock(name: str):
    """
    Load JSON mock from tests/mock/
    """
    path = MOCK_DIR / f"{name}.json"

    if not path.exists():
        raise FileNotFoundError(f"Mock not found: {path}")

    return json.loads(path.read_text())