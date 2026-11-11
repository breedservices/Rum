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

import datetime
import pathlib
import re
import warnings
from importlib.metadata import PackageNotFoundError, version

from typing_extensions import TypedDict, deprecated

__all__ = ("__version__", "VersionInfo", "version_info")

from typing import Literal, NamedTuple


def _read_fallback_version() -> str:
    """Read the version declared in ``pyproject.toml``.

    This is only used when the package is not installed, so that running
    straight from a source checkout still reports a sensible version.
    """
    pyproject = pathlib.Path(__file__).resolve().parent.parent / "pyproject.toml"
    try:
        content = pyproject.read_text(encoding="utf-8")
    except OSError:
        return "0.0.0"

    match = re.search(r'^version\s*=\s*"([^"]+)"', content, flags=re.MULTILINE)
    return match.group(1) if match else "0.0.0"


_FALLBACK_VERSION = _read_fallback_version()

try:
    __version__ = version("rum")
except PackageNotFoundError:
    # The package is not installed (e.g. running straight from a source
    # checkout). Fall back to the version declared in pyproject.toml.
    __version__ = _FALLBACK_VERSION
    warnings.warn(
        (
            "Package is not installed. "
            f"As a fallback, {__name__}.__version__ will be set to {__version__}"
        ),
        RuntimeWarning,
        stacklevel=2,
    )


class AdvancedVersionInfo(TypedDict):
    serial: int
    build: int | None
    commit: str | None
    date: datetime.date | None


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]

    # We can't set instance attributes on a NamedTuple, so we have to use a
    # global variable to store the advanced version info.
    @property
    def advanced(self) -> AdvancedVersionInfo:
        return _advanced

    @advanced.setter
    def advanced(self, value: object) -> None:
        global _advanced
        _advanced = value

    @property
    @deprecated(
        "VersionInfo.release_level is deprecated since version 2.4, consider using releaselevel instead."
    )
    def release_level(self) -> Literal["alpha", "beta", "candidate", "final"]:
        return self.releaselevel

    @property
    @deprecated(
        'VersionInfo.serial is deprecated since version 2.4, consider using .advanced["serial"] instead.'
    )
    def serial(self) -> int:
        return self.advanced["serial"]

    @property
    @deprecated(
        'VersionInfo.build is deprecated since version 2.4, consider using .advanced["build"] instead.'
    )
    def build(self) -> int | None:
        return self.advanced["build"]

    @property
    @deprecated(
        'VersionInfo.commit is deprecated since version 2.4, consider using .advanced["commit"] instead.'
    )
    def commit(self) -> str | None:
        return self.advanced["commit"]

    @property
    @deprecated(
        'VersionInfo.date is deprecated since version 2.4, consider using .advanced["date"] instead.'
    )
    def date(self) -> datetime.date | None:
        return self.advanced["date"]


version_regex = re.compile(
    r"^(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?"
    r"(?:(?P<level>rc|a|b)(?P<serial>\d+))?"
    r"(?:\.dev(?P<build>\d+))?"
    r"(?:\+(?:(?:g(?P<commit>[a-fA-F0-9]{4,40})(?:\.d(?P<date>\d{4}\d{2}\d{2})|))|d(?P<date1>\d{4}\d{2}\d{2})))?$"
)
version_match = version_regex.match(__version__)
if version_match is None:
    raise RuntimeError(f"Invalid version string: {__version__}")
raw_info = version_match.groupdict()

level_info: Literal["alpha", "beta", "candidate", "final"]

if raw_info["level"] == "a":
    level_info = "alpha"
elif raw_info["level"] == "b":
    level_info = "beta"
elif raw_info["level"] == "rc":
    level_info = "candidate"
elif raw_info["level"] is None:
    level_info = "final"
else:
    raise RuntimeError("Invalid release level")

if (raw_date := raw_info["date"] or raw_info["date1"]) is not None:
    date_info = datetime.date(
        int(raw_date[:4]),
        int(raw_date[4:6]),
        int(raw_date[6:]),
    )
else:
    date_info = None

version_info: VersionInfo = VersionInfo(
    major=int(raw_info["major"]) if raw_info["major"] is not None else None,
    minor=int(raw_info["minor"]) if raw_info["minor"] is not None else None,
    micro=int(raw_info["patch"]) if raw_info["patch"] is not None else None,
    releaselevel=level_info,
)

_advanced = AdvancedVersionInfo(
    serial=raw_info["serial"],
    build=int(raw_info["build"]) if raw_info["build"] is not None else None,
    commit=raw_info["commit"],
    date=date_info,
)
