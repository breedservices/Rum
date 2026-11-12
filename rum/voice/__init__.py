"""
discord.voice
~~~~~~~~~~~~~

Voice support for the Discord API.

:copyright: (c) 2015-2021 Rapptz & (c) 2021-present Pycord Development
:copyright: (c) 2026-present The rum team
:license: MIT, see LICENSE for more details.
"""

from ..errors import MissingVoiceDependenciesError
from ..utils import get_missing_voice_dependencies

if missing := get_missing_voice_dependencies():
    raise MissingVoiceDependenciesError(missing=missing)

from ._types import *
from .client import *
from .packets import *
