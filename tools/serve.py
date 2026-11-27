#!/usr/bin/env python3
"""Tiny static server with the MIME types required by ONNX Runtime Web.

Usage:
    python tools/serve.py            # http://127.0.0.1:8123/main.html

Python's default http.server reports .mjs as text/plain, which breaks ES module
imports used by onnxruntime-web 1.22. This server also avoids the unstable
Cache API behaviour of file:// URLs.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import os
import socketserver

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXTRA_TYPES = {
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".wasm": "application/wasm",
    ".data": "application/octet-stream",
    ".json": "application/json",
    ".gz": "application/gzip",
}


class Handler(http.server.SimpleHTTPRequestHandler):
    def guess_type(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        if ext in EXTRA_TYPES:
            return EXTRA_TYPES[ext]
        return super().guess_type(path)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8123)
    parser.add_argument("--bind", default="127.0.0.1")
    args = parser.parse_args()

    handler = functools.partial(Handler, directory=ROOT)
    with socketserver.TCPServer((args.bind, args.port), handler) as httpd:
        print(f"Serving {ROOT} at http://{args.bind}:{args.port}/main.html", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
