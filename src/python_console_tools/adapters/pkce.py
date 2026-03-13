import base64
import hashlib
import os
import secrets
from dataclasses import dataclass


@dataclass
class PKCECodes:
    verifier: str
    challenge: str


def generate_pkce() -> PKCECodes:
    verifier_bytes = secrets.token_urlsafe(64)
    verifier = verifier_bytes[:128]
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("utf-8")).digest())
        .rstrip(b"=")
        .decode("ascii")
    )
    return PKCECodes(verifier=verifier, challenge=challenge)
