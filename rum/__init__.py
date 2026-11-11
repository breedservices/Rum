"""
rum - Discord API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~

rum is a fork of Pycord, maintained by The rum team.

:copyright: (c) 2015-2021 Rapptz & (c) 2021-present Pycord Development
:copyright: (c) 2026-present The rum team
:license: MIT, see LICENSE for more details.
"""

__title__ = "rum"
__author__ = "The rum team"
__license__ = "MIT"
__copyright__ = "Copyright 2015-2021 Rapptz & Copyright 2021-present Pycord Development & Copyright 2026-present The rum team"

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

import logging
from typing import TYPE_CHECKING

# We need __version__ to be imported first
# isort: off
from ._version import *

# isort: on


from . import abc, opus, sinks, ui, utils
from .activity import *
from .appinfo import *
from .application_role_connection import *
from .asset import *
from .audit_logs import *
from .automod import *
from .bot import *
from .cache import *
from .channel import *
from .client import *
from .cog import *
from .collectibles import *
from .colour import *
from .commands import *
from .components import *
from .embeds import *
from .emoji import *
from .enums import *
from .errors import *
from .file import *
from .flags import *
from .guild import *
from .http import *
from .incidents import *
from .integrations import *
from .interactions import *
from .invite import *
from .member import *
from .mentions import *
from .message import *
from .monetization import *
from .object import *
from .onboarding import *
from .partial_emoji import *
from .permissions import *
from .player import *
from .poll import *
from .primary_guild import *
from .raw_models import *
from .reaction import *
from .role import *
from .scheduled_events import *
from .shard import *
from .shared_client_theme import *
from .soundboard import *
from .stage_instance import *
from .sticker import *
from .team import *
from .template import *
from .threads import *
from .user import *
from .webhook import *
from .welcome_screen import *
from .widget import *

if TYPE_CHECKING:
    from typing import Generic, TypeVar

    from typing_extensions import deprecated

    from rum.voice import VoiceClient as VoiceClientC
    from rum.voice import VoiceProtocol as VoiceProtocolC

    C = TypeVar("C", bound=Client)

    @deprecated(
        "rum.VoiceClient is deprecated in favour of rum.voice.VoiceClient since 2.7 and will be removed in 3.0",
    )
    class VoiceClient(VoiceClientC): ...

    @deprecated(
        "rum.VoiceProtocol is deprecated in favour of rum.voice.VoiceProtocol since 2.7 and will be removed in 3.0",
    )
    class VoiceProtocol(VoiceProtocolC[C], Generic[C]): ...

else:
    from .utils import warn_deprecated

    def __getattr__(name: str) -> object:
        if name == "VoiceClient":
            warn_deprecated(
                "rum.VoiceClient", "rum.voice.VoiceClient", "2.7", "3.0"
            )
            from .voice import VoiceClient

            return VoiceClient
        if name == "VoiceProtocol":
            warn_deprecated(
                "rum.VoiceProtocol", "rum.voice.VoiceProtocol", "2.7", "3.0"
            )
            from .voice import VoiceProtocol

            return VoiceProtocol
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


logging.getLogger(__name__).addHandler(logging.NullHandler())
