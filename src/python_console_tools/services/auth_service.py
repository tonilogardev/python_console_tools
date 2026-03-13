from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx

from python_console_tools.adapters.auth0 import Auth0Client
from python_console_tools.adapters.local_server import run_once
from python_console_tools.adapters.pkce import generate_pkce
from python_console_tools.adapters.token_store import TokenPair, clear_tokens, load_tokens, save_tokens
from python_console_tools.settings import Settings


class AuthError(RuntimeError):
    pass


class AuthService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._base = f"https://{settings.auth0_domain}" if settings.auth0_domain else ""
        self.client = Auth0Client(
            domain=settings.auth0_domain or "",
            client_id=settings.auth0_client_id or "",
            audience=settings.auth0_audience or "",
        )

    def _client(self) -> httpx.Client:
        return httpx.Client(timeout=15)

    def start_device_flow(self) -> Dict[str, Any]:
        self._ensure_config()
        return self.client.device_code()

    def start_pkce_flow(self) -> TokenPair:
        self._ensure_config()
        pkce = generate_pkce()
        redirect_uri = f"http://{self.settings.auth_redirect_host}:{self.settings.auth_redirect_port}/callback"
        url = self.client.authorize_url(
            redirect_uri=redirect_uri,
            code_challenge=pkce.challenge,
            prompt="login",
        )

        import webbrowser

        webbrowser.open(url)
        result = run_once(self.settings.auth_redirect_host, self.settings.auth_redirect_port, timeout=self.settings.auth_poll_timeout)
        if result.error:
            raise AuthError(result.error)
        if not result.code:
            raise AuthError("No code received (timeout o cancelado)")

        data = self.client.token_with_pkce(code=result.code, code_verifier=pkce.verifier, redirect_uri=redirect_uri)
        token = TokenPair(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            id_token=data.get("id_token"),
        )
        save_tokens(token)
        return token

    def poll_device_flow(self, device_code: str, interval: int) -> TokenPair:
        self._ensure_config()
        start = time.time()
        while True:
            if time.time() - start > self.settings.auth_poll_timeout:
                raise AuthError("Device flow timeout")
            resp = self.client.poll_device(device_code)
            if resp.status_code == 200:
                data = resp.json()
                token = TokenPair(
                    access_token=data["access_token"],
                    refresh_token=data.get("refresh_token"),
                    id_token=data.get("id_token"),
                )
                save_tokens(token)
                return token
            payload_err = resp.json()
            if resp.status_code == 428 or payload_err.get("error") in {"authorization_pending"}:
                time.sleep(interval)
                continue
            if payload_err.get("error") == "slow_down":
                interval += 5
                time.sleep(interval)
                continue
            resp.raise_for_status()

    def refresh(self) -> TokenPair:
        self._ensure_config()
        tokens = load_tokens()
        if not tokens or not tokens.refresh_token:
            raise AuthError("No refresh token stored")
        data = self.client.refresh(tokens.refresh_token)
        new_tokens = TokenPair(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", tokens.refresh_token),
            id_token=data.get("id_token"),
        )
        save_tokens(new_tokens)
        return new_tokens

    def signup(self, email: str, password: str) -> str:
        self._ensure_config()
        try:
            resp = self.client.signup_db(
                email=email,
                password=password,
                connection=self.settings.auth0_db_connection,
            )
            return resp.get("_id", "created")
        except httpx.HTTPStatusError as exc:
            msg = exc.response.text
            raise AuthError(f"Signup failed: {msg}") from exc

    def userinfo(self) -> Dict[str, Any]:
        tokens = load_tokens()
        if not tokens:
            raise AuthError("Not logged in")
        try:
            return self.client.userinfo(tokens.access_token)
        except httpx.HTTPStatusError:
            refreshed = self.refresh()
            return self.client.userinfo(refreshed.access_token)

    def status(self) -> str:
        tokens = load_tokens()
        if not tokens:
            return "Not logged in"
        try:
            info = self.userinfo()
            return f"Logged in as {info.get('email') or info.get('sub')}"
        except Exception:
            return "Logged in (token stored)"

    def logout(self) -> None:
        clear_tokens()

    def _ensure_config(self) -> None:
        missing = [k for k in ["auth0_domain", "auth0_client_id", "auth0_audience"] if not getattr(self.settings, k)]
        if missing:
            raise AuthError(f"Missing Auth0 settings: {', '.join(missing)}")
