from __future__ import annotations

from typing import Any, Dict

import httpx


class Auth0Client:
    def __init__(self, domain: str, client_id: str, audience: str, timeout: int = 15) -> None:
        self.base = f"https://{domain}"
        self.client_id = client_id
        self.audience = audience
        self.timeout = timeout

    def device_code(self, scope: str = "offline_access openid profile email") -> Dict[str, Any]:
        payload = {"client_id": self.client_id, "audience": self.audience, "scope": scope}
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base}/oauth/device/code", data=payload)
            resp.raise_for_status()
            return resp.json()

    def authorize_url(self, redirect_uri: str, code_challenge: str, scope: str = "openid profile email offline_access") -> str:
        from urllib.parse import urlencode

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "audience": self.audience,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        return f"{self.base}/authorize?{urlencode(params)}"

    def token_with_pkce(self, code: str, code_verifier: str, redirect_uri: str) -> Dict[str, Any]:
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "code_verifier": code_verifier,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base}/oauth/token", data=payload)
            resp.raise_for_status()
            return resp.json()

    def poll_device(self, device_code: str) -> Dict[str, Any]:
        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
            "client_id": self.client_id,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base}/oauth/token", data=payload)
            return resp

    def refresh(self, refresh_token: str) -> Dict[str, Any]:
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": refresh_token,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base}/oauth/token", data=payload)
            resp.raise_for_status()
            return resp.json()

    def signup_db(self, email: str, password: str, connection: str) -> Dict[str, Any]:
        payload = {
            "client_id": self.client_id,
            "email": email,
            "password": password,
            "connection": connection,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base}/dbconnections/signup", json=payload)
            resp.raise_for_status()
            return resp.json()

    def userinfo(self, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{self.base}/userinfo", headers=headers)
            resp.raise_for_status()
            return resp.json()
