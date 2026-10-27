#!/usr/bin/env python3
"""Serve the game in ./game on http://127.0.0.1:8000 and open it in the browser.

    python3 serve.py [port]
"""
import functools
import http.server
import mimetypes
import sys
import webbrowser
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
GAME = Path(__file__).resolve().parent / "game"

mimetypes.add_type("model/gltf-binary", ".glb")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("application/wasm", ".wasm")

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(GAME))
with http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler) as httpd:
    url = "http://127.0.0.1:%d/" % PORT
    print("Old City Walker on %s  (Ctrl+C to stop)" % url)
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
