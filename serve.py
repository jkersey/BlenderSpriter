#!/usr/bin/env python3
"""Serve the scripts directory with render-tool API endpoints."""

import json
import os
import subprocess
from configparser import ConfigParser
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingTCPServer

RENDER_DIR = Path("render")
CONFIG_FILE = Path("config.ini")
MODELS_DIR = Path("models")


def build_model_map():
    """Return {blend_stem: directory} for every .blend file under models/."""
    result = {}
    for blend in MODELS_DIR.rglob("*.blend"):
        if not blend.suffix == ".blend":
            continue
        result[blend.stem] = blend.parent
    return result


def find_skin_path(render_name: str) -> str | None:
    """Resolve the skin PNG for a render output directory name."""
    model_map = build_model_map()
    parts = render_name.split("_")
    # Try longest-prefix match first (e.g. wall_desert_tech | default)
    for i in range(len(parts) - 1, 0, -1):
        stem = "_".join(parts[:i])
        skin = "_".join(parts[i:])
        if stem in model_map:
            candidate = model_map[stem] / f"{skin}.png"
            if candidate.exists():
                return str(candidate)
    return None


def scan_renders():
    if not RENDER_DIR.exists():
        return {}

    result = {}
    for model_dir in sorted(RENDER_DIR.iterdir()):
        if not model_dir.is_dir():
            continue

        top_pngs = sorted(p.name for p in model_dir.glob("*.png"))
        subdirs = [d for d in model_dir.iterdir() if d.is_dir()]

        skin_path = find_skin_path(model_dir.name)

        if top_pngs and not subdirs:
            result[model_dir.name] = {
                "type": "static",
                "frames": top_pngs,
                "skin": skin_path,
            }
        else:
            stations = {}
            for station_dir in sorted(subdirs):
                actions = {}
                for action_dir in sorted(
                    d for d in station_dir.iterdir() if d.is_dir()
                ):
                    directions = {}
                    for dir_dir in sorted(
                        d for d in action_dir.iterdir() if d.is_dir()
                    ):
                        frames = sorted(p.name for p in dir_dir.glob("*.png"))
                        if frames:
                            directions[dir_dir.name] = frames
                    if directions:
                        actions[action_dir.name] = directions
                if actions:
                    stations[station_dir.name] = actions
            if stations:
                result[model_dir.name] = {
                    "type": "character",
                    "stations": stations,
                    "skin": skin_path,
                }

    return result


def read_config():
    config = ConfigParser()
    config.read(CONFIG_FILE)
    return {
        "active": (
            dict(config.items("directions")) if config.has_section("directions") else {}
        ),
        "inactive": (
            dict(config.items("unused")) if config.has_section("unused") else {}
        ),
    }


def toggle_direction(name: str, active: bool):
    config = ConfigParser()
    config.read(CONFIG_FILE)

    src, dst = ("unused", "directions") if active else ("directions", "unused")

    if not config.has_section(src) or not config.has_option(src, name):
        return  # nothing to do

    val = config.get(src, name)
    config.remove_option(src, name)
    if not config.has_section(dst):
        config.add_section(dst)
    config.set(dst, name, val)

    with open(CONFIG_FILE, "w") as f:
        config.write(f)


class Handler(SimpleHTTPRequestHandler):

    # ── GET ──────────────────────────────────────────────────────────────────

    def do_GET(self):
        if self.path == "/api/renders":
            self._json(scan_renders())
        elif self.path == "/api/config":
            self._json(read_config())
        else:
            super().do_GET()

    # ── POST ─────────────────────────────────────────────────────────────────

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if self.path == "/api/config/toggle":
            toggle_direction(body["name"], body["active"])
            self._json({"ok": True})

        elif self.path == "/api/render":
            result = subprocess.run(
                ["./render.sh"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent,
            )
            self._json(
                {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                }
            )

        else:
            self.send_error(404)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _json(self, data):
        payload = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        if args and str(args[1]) not in ("200", "304"):
            super().log_message(format, *args)


class Server(ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    port = 8080
    os.chdir(Path(__file__).parent)
    server = Server(("localhost", port), Handler)
    print(f"Serving at http://localhost:{port}/index.html")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
