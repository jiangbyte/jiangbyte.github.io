#!/usr/bin/env python3
"""Local cover-review UI + ycy resolve proxy (avoids browser CORS).

  python3 scripts/cover-review-server.py
  # open http://127.0.0.1:8765/
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "cover-review.html"
YCY = "https://t.alcy.cc/ycy"
HOST, PORT = "127.0.0.1", 8765


def resolve_ycy() -> str:
    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)

    opener = urllib.request.build_opener(NoRedir)
    req = urllib.request.Request(YCY, method="GET")
    try:
        opener.open(req, timeout=20)
    except urllib.error.HTTPError as he:
        if he.code in (301, 302, 303, 307, 308):
            loc = he.headers.get("Location") or ""
            if loc.startswith("/"):
                return "https://t.alcy.cc" + loc
            if loc.startswith("http"):
                return loc
        raise
    raise RuntimeError("ycy did not redirect")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html", "/cover-review.html"):
            data = HTML.read_bytes()
            self._send(200, data, "text/html; charset=utf-8")
            return
        if path == "/api/ycy":
            try:
                url = resolve_ycy()
                payload = json.dumps({"url": url}, ensure_ascii=False).encode("utf-8")
                self._send(200, payload, "application/json; charset=utf-8")
            except Exception as e:  # noqa: BLE001
                payload = json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8")
                self._send(502, payload, "application/json; charset=utf-8")
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")


def main() -> None:
    if not HTML.exists():
        raise SystemExit(f"missing {HTML}")
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Cover review: http://{HOST}:{PORT}/")
    print("Each「换一张」calls /api/ycy → resolves https://t.alcy.cc/ycy to a stable URL.")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
