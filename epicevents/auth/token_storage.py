from pathlib import Path
from typing import Optional

APP_NAME = ".epicevents"
TOKEN_FILENAME = "token"


def get_token_path() -> Path:
    return Path.home() / APP_NAME / TOKEN_FILENAME


def save_token(token: str) -> Path:
    token_path = get_token_path()
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(token)
    return token_path


def load_token() -> Optional[str]:
    token_path = get_token_path()
    if not token_path.exists():
        return None
    return token_path.read_text().strip() or None


def delete_token() -> bool:
    token_path = get_token_path()
    if token_path.exists():
        token_path.unlink()
        return True
    return False