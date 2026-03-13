from pathlib import Path
import json
from typing import Any, Dict

from python_console_tools.settings import Settings


class AuthService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._token_path = Path.home() / ".python_console_tools" / "auth.json"
        self._token_path.parent.mkdir(parents=True, exist_ok=True)

    def login(self, username: str, password: str) -> str:
        token = f"token-for-{username}"
        self._store_token(token)
        return token

    def signup(self, username: str, password: str) -> str:
        # Placeholder: create user remotely; here we just simulate.
        token = f"token-for-{username}"
        self._store_token(token)
        return token

    def status(self) -> str:
        if self._token_path.exists():
            data = json.loads(self._token_path.read_text(encoding="utf-8"))
            return f"Logged in as {data.get('user','unknown')}"
        return "Not logged in"

    def _store_token(self, token: str) -> None:
        payload: Dict[str, Any] = {"token": token, "user": self.settings.user or "unknown"}
        self._token_path.write_text(json.dumps(payload), encoding="utf-8")
