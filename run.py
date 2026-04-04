#!/usr/bin/env python3
"""
Launcher for the Spriter render pipeline.

Usage: python run.py

This script validates prerequisites (Blender on PATH, config.ini present)
before invoking Blender to render the sprite sheets. Use this instead of
calling render.py directly.
"""
import subprocess
import sys
import os

# Import prerequisite checks from render.py
sys.path.insert(0, os.path.dirname(__file__))
from render import check_blender, load_config


def main():
    check_blender()
    config = load_config()

    blender_file = config.get("config", "blender_file", fallback=None)
    if blender_file is None:
        print("Error: 'blender_file' not set in config.ini under [config]")
        sys.exit(1)

    print(f"Launching Blender with: {blender_file}")
    subprocess.run([
        "blender", blender_file, "--background", "--python", "render.py"
    ], check=True)


if __name__ == "__main__":
    main()
