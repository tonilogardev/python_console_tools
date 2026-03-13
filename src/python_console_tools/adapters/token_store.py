from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

try:
    import keyring
except ImportError:  # pragma: no cover - optional dep fallback handled
    keyring = None  # type: ignore


SERVICE_NAME = "python_console_tools"
FALLBACK_PATH = Path.home() / ".python_console_tools" / "auth.json"


class TokenPair:
    def __init__(self, access_token: str, refresh_token: Optional[str] = None, id_token: Optional[str] = None) -> None:
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.id_token = id_token

    def to_json(self) -> str:
        return json.dumps(
            {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "id_token": self.id_token,
            }
        )

    @classmethod
    def from_json(cls, data: str) -> "TokenPair":
        obj = json.loads(data)
        return cls(obj["access_token"], obj.get("refresh_token"), obj.get("id_token"))


def save_tokens(token_pair: TokenPair) -> None:
    if keyring:
        keyring.set_password(SERVICE_NAME, "tokens", token_pair.to_json())
        return

    FALLBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FALLBACK_PATH, "w", encoding="utf-8") as fh:
        fh.write(token_pair.to_json())
    os.chmod(FALLBACK_PATH, 0o600)


def load_tokens() -> Optional[TokenPair]:
    if keyring:
        data = keyring.get_password(SERVICE_NAME, "tokens")
        if data:
            return TokenPair.from_json(data)
        return None

    if FALLBACK_PATH.exists():
        return TokenPair.from_json(FALLBACK_PATH.read_text(encoding="utf-8"))
    return None


def clear_tokens() -> None:
    if keyring:
        try:
            keyring.delete_password(SERVICE_NAME, "tokens")
        except keyring.errors.PasswordDeleteError:
            pass
    if FALLBACK_PATH.exists():
        FALLBACK_PATH.unlink()
