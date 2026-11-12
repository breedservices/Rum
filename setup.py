"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-2026 Pycord Development
Copyright (c) 2026-present The rum team

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import sys
from pathlib import Path

from setuptools import setup

# Packaging entry point.
#
# Most metadata lives in ``pyproject.toml``. The summary and keywords are
# derived from ``README.md`` so there is a single source of truth.

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

try:
    from readme_metadata import read_metadata
except ImportError:  # pragma: no cover - fallback if the script is missing
    metadata = {
        "description": "rum - a Discord API wrapper for Python, forked from Pycord",
        "keywords": ["discord", "discord-bot", "python", "async", "pycord", "rum"],
    }
else:
    metadata = read_metadata(ROOT / "README.md")


if __name__ == "__main__":
    setup(
        description=metadata["description"],
        keywords=list(metadata["keywords"]),
    )
