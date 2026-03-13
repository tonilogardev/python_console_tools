from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx

from python_console_tools.adapters.token_store import TokenPair, clear_tokens, load_tokens, save_tokens
from python_console_tools.settings import Settings


class AuthError(RuntimeError):
    pass


class AuthService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._base = f"https://{settings.auth0_domain}" if settings.auth0_domain else ""

    def _client(self) -> httpx.Client:
        return httpx.Client(timeout=15)

    def start_device_flow(self) -> Dict[str, Any]:
        self._ensure_config()
        payload = {
            "client_id": self.settings.auth0_client_id,
            "audience": self.settings.auth0_audience,
            "scope": "offline_access openid profile email",
        }
        with self._client() as client:
            resp = client.post(f"{self._base}/oauth/device/code", data=payload)
            resp.raise_for_status()
            return resp.json()

    def poll_device_flow(self, device_code: str, interval: int) -> TokenPair:
        self._ensure_config()
        start = time.time()
        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
            "client_id": self.settings.auth0_client_id,
        }
        with self._client() as client:
            while True:
                if time.time() - start > self.settings.auth_poll_timeout:
                    raise AuthError("Device flow timeout")
                resp = client.post(f"{self._base}/oauth/token", data=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    token = TokenPair(
                        access_token=data["access_token"],
                        refresh_token=data.get("refresh_token"),
                        id_token=data.get("id_token"),
                    )
                    save_tokens(token)
                    return token
                if resp.status_code == 428 or resp.json().get("error") in {"authorization_pending"}:
                    time.sleep(interval)
                    continue
                if resp.json().get("error") == "slow_down":
                    interval += 5
                    time.sleep(interval)
                    continue
                resp.raise_for_status()

    def refresh(self) -> TokenPair:
        self._ensure_config()
        tokens = load_tokens()
        if not tokens or not tokens.refresh_token:
            raise AuthError("No refresh token stored")
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.settings.auth0_client_id,
            "refresh_token": tokens.refresh_token,
        }
        with self._client() as client:
            resp = client.post(f"{self._base}/oauth/token", data=payload)
            resp.raise_for_status()
            data = resp.json()
            new_tokens = TokenPair(
                access_token=data["access_token"],
                refresh_token=data.get("refresh_token", tokens.refresh_token),
                id_token=data.get("id_token"),
            )
            save_tokens(new_tokens)
            return new_tokens

    def status(self) -> str:
        tokens = load_tokens()
        if not tokens:
            return "Not logged in"
        return "Logged in (access token stored)"

    def logout(self) -> None:
        clear_tokens()

    def _ensure_config(self) -> None:
        missing = [k for k in ["auth0_domain", "auth0_client_id", "auth0_audience"] if not getattr(self.settings, k)]
        if missing:
            raise AuthError(f"Missing Auth0 settings: {', '.join(missing)}")
