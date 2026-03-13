from __future__ import annotations

import http.server
import socket
import threading
from dataclasses import dataclass
from typing import Optional


@dataclass
class CallbackResult:
    code: Optional[str]
    error: Optional[str]


class _Handler(http.server.BaseHTTPRequestHandler):
    result: CallbackResult  # type: ignore
    event: threading.Event  # type: ignore

    def do_GET(self) -> None:  # noqa: N802
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        code = qs.get("code", [None])[0]
        error = qs.get("error", [None])[0]
        self.__class__.result.code = code
        self.__class__.result.error = error
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h2>Authentication complete. You can close this window.</h2></body></html>")
        self.__class__.event.set()

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def run_once(host: str, port: int, timeout: int = 300) -> CallbackResult:
    result = CallbackResult(code=None, error=None)
    event = threading.Event()
    handler = _Handler
    handler.result = result  # type: ignore
    handler.event = event  # type: ignore

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)

    server = http.server.HTTPServer((host, port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    event.wait(timeout=timeout)
    server.shutdown()
    thread.join()
    return result
