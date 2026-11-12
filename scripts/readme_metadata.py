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
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Derive package/repository metadata from README.md.
#
# README.md is the single source of truth for the project's summary and
# keywords. This script parses it and can either print the derived values
# or push them to the GitHub repository so the "About" section and topics
# stay in sync with the README.
#
# Usage:
#     python scripts/readme_metadata.py            # print JSON to stdout
#     python scripts/readme_metadata.py --summary  # print the summary only
#     python scripts/readme_metadata.py --apply    # update the GitHub repo

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

# Front matter style key/value pairs are read from an HTML comment at the top
# of the README so the raw file still renders nicely on GitHub.
FRONT_MATTER_RE = re.compile(
    r"<!--\s*readme-metadata\s*\n(?P<body>.*?)\n-->", re.DOTALL | re.MULTILINE
)
KEY_VALUE_RE = re.compile(r"^\s*(?P<key>[A-Za-z0-9_-]+)\s*:\s*(?P<value>.*?)\s*$")
HEADING_RE = re.compile(r"^#\s+(?P<title>.+?)\s*$", re.MULTILINE)

# The first non-empty paragraph after the title is used as the fallback
# description when the front matter does not provide one.
FALLBACK_DESCRIPTION = "rum - a Discord API wrapper for Python, forked from Pycord"

MAX_DESCRIPTION_LENGTH = 350
MAX_KEYWORDS = 20


def _strip_markdown(text: str) -> str:
    """Remove common Markdown/HTML constructs from a string."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # links
    text = re.sub(r"`([^`]*)`", r"\1", text)  # inline code
    text = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", text)  # bold/italic
    text = re.sub(r"<[^>]+>", "", text)  # html tags
    return re.sub(r"\s+", " ", text).strip()


def parse_front_matter(readme: str) -> dict[str, str]:
    """Parse the ``<!-- readme-metadata -->`` block into a dict."""
    match = FRONT_MATTER_RE.search(readme)
    if match is None:
        return {}

    data: dict[str, str] = {}
    for line in match.group("body").splitlines():
        kv = KEY_VALUE_RE.match(line)
        if kv is None:
            continue
        key = kv.group("key").lower()
        value = kv.group("value").strip().strip("'\"")
        if value:
            data[key] = value
    return data


def parse_title(readme: str) -> str:
    """Return the first top-level Markdown heading."""
    match = HEADING_RE.search(readme)
    return match.group("title").strip() if match else "rum"


def parse_description(readme: str, front_matter: dict[str, str]) -> str:
    """Return the package summary."""
    if "description" in front_matter:
        description = _strip_markdown(front_matter["description"])
    else:
        description = ""

    if not description:
        # Fall back to the first paragraph after the heading.
        body = HEADING_RE.sub("", readme, count=1)
        for block in re.split(r"\n\s*\n", body):
            candidate = _strip_markdown(block)
            if candidate and not candidate.startswith("#"):
                description = candidate
                break

    description = description or FALLBACK_DESCRIPTION
    if len(description) > MAX_DESCRIPTION_LENGTH:
        description = description[: MAX_DESCRIPTION_LENGTH - 1].rstrip() + "…"
    return description


def parse_keywords(readme: str, front_matter: dict[str, str]) -> list[str]:
    """Return the list of keywords/topic tags."""
    raw = front_matter.get("keywords") or front_matter.get("topics") or ""
    keywords = [k.strip() for k in raw.split(",") if k.strip()]
    return keywords[:MAX_KEYWORDS]


def parse_homepage(readme: str, front_matter: dict[str, str]) -> str:
    """Return the homepage URL if one was declared."""
    return front_matter.get("homepage", "").strip()


def read_metadata(path: Path = README) -> dict[str, object]:
    """Read README.md and return the derived metadata."""
    readme = path.read_text(encoding="utf-8")
    front_matter = parse_front_matter(readme)
    return {
        "title": parse_title(readme),
        "description": parse_description(readme, front_matter),
        "keywords": parse_keywords(readme, front_matter),
        "homepage": parse_homepage(readme, front_matter),
    }


def _github_request(url: str, method: str = "GET", payload: dict | None = None) -> dict:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required to update the repository metadata.")

    repository = os.environ.get("GITHUB_REPOSITORY")
    if not repository:
        raise SystemExit("GITHUB_REPOSITORY is not set.")

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "rum-readme-metadata",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:  # nosec B310
            body = response.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise SystemExit(f"GitHub API error {exc.code}: {detail}") from exc


def apply_to_github(metadata: dict[str, object]) -> None:
    """Push the derived metadata to the GitHub repository."""
    repository = os.environ.get("GITHUB_REPOSITORY")
    if not repository:
        raise SystemExit("GITHUB_REPOSITORY is not set.")

    api = f"https://api.github.com/repos/{repository}"
    payload: dict[str, object] = {"description": metadata["description"]}
    homepage = metadata.get("homepage")
    if homepage:
        payload["homepage"] = homepage

    print(f"Updating description for {repository}…")
    _github_request(api, method="PATCH", payload=payload)

    keywords = metadata.get("keywords") or []
    if keywords:
        print(f"Updating topics: {', '.join(keywords)}")
        _github_request(
            f"{api}/topics",
            method="PUT",
            payload={"names": list(keywords)},
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true", help="print the summary only")
    parser.add_argument("--apply", action="store_true", help="update the GitHub repository")
    parser.add_argument(
        "--readme", type=Path, default=README, help="path to README.md"
    )
    args = parser.parse_args(argv)

    metadata = read_metadata(args.readme)

    if args.summary:
        print(metadata["description"])
        return 0

    if args.apply:
        apply_to_github(metadata)
        return 0

    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
