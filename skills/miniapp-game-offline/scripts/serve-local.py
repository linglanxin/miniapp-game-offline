"""Serve an uncompressed local game on a stable loopback URL."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from urllib.parse import quote
import webbrowser


class GameHandler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".wasm": "application/wasm",
        ".data": "application/octet-stream",
        ".bundle": "application/octet-stream",
    }

    def send_head(self):
        target = Path(self.translate_path(self.path)).resolve()
        if not target.is_relative_to(Path(self.directory)):
            self.send_error(403, "Resource outside the game directory")
            return None
        return super().send_head()

    def list_directory(self, path):
        self.send_error(404, "Open the game entry page")
        return None

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--entry", default="index.html")
    parser.add_argument("--port", type=int, default=18742)
    parser.add_argument("--open", action="store_true", help="Open the game in the default browser")
    args = parser.parse_args()

    root = args.directory.resolve()
    entry = (root / args.entry).resolve()
    if not entry.is_relative_to(root) or not entry.is_file():
        parser.error("The entry file must exist inside the game directory")
    if not 1 <= args.port <= 65535:
        parser.error("Choose a stable port between 1 and 65535")
    bind = ("127.0.0.1", args.port)
    try:
        server = ThreadingHTTPServer(bind, partial(GameHandler, directory=str(root)))
    except OSError as error:
        print(f"Cannot start local game server: {error}", file=sys.stderr)
        return 1
    url = f"http://{bind[0]}:{bind[1]}/{quote(entry.relative_to(root).as_posix())}"
    with server:
        print(url, flush=True)
        if args.open:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
