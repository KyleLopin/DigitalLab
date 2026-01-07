# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""
Add the proper paths to sys.path, so I can import normally and see proper typehints
and still run manim from terminal.
"""

__author__ = "Kyle Vitautas Lopin"

import sys
from pathlib import Path

# --- add local project folders to sys.path ---
LOGIC_DIR = Path(__file__).resolve().parent                 # .../manim_scripts/logic
MANIM_SCRIPTS_DIR = LOGIC_DIR.parent                        # .../manim_scripts
HELPERS_DIR = MANIM_SCRIPTS_DIR / "helpers"                 # .../manim_scripts/helpers

for p in (LOGIC_DIR, MANIM_SCRIPTS_DIR, HELPERS_DIR):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)
