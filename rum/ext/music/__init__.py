"""
rum.ext.music
~~~~~~~~~~~~~

A Lavalink v4 and NodeLink v3 music client for rum.

Uses rum's transport (no aiohttp, no voice extra). Choose the server protocol at
init with ``server_type="lavalink"`` or ``server_type="nodelink"``.

Players accept a custom queue provider via ``queue=...`` (default: in-memory
:class:`~rum.ext.music.Queue`) so queue state can be stored outside RAM.
"""

from .enums import *
from .events import *
from .exceptions import *
from .filters import *
from .node import *
from .objects import *
from .player import *
from .pool import *
from .queue import *

__all__ = (
    "AudioFading",
    "ChannelMix",
    "Chorus",
    "Compressor",
    "Distortion",
    "Echo",
    "Equalizer",
    "FadeCurve",
    "Filter",
    "Filters",
    "HighPass",
    "Karaoke",
    "LoadResult",
    "LoadType",
    "LowPass",
    "MusicEvent",
    "MusicException",
    "NoNodesAvailable",
    "Node",
    "NodeConnectedEvent",
    "NodeDisconnectedEvent",
    "NodeEvent",
    "NodeException",
    "NodeNotAvailable",
    "NodePool",
    "Phaser",
    "Player",
    "PlayerConnectedEvent",
    "PlayerCreatedEvent",
    "PlayerDestroyedEvent",
    "PlayerException",
    "PlayerReconnectingEvent",
    "PlayerUpdateEvent",
    "Playlist",
    "Queue",
    "QueueEmpty",
    "Rotation",
    "SearchType",
    "ServerType",
    "Spatial",
    "Timescale",
    "Track",
    "TrackEndEvent",
    "TrackEndReason",
    "TrackExceptionEvent",
    "TrackLoadError",
    "TrackStartEvent",
    "TrackStuckEvent",
    "Tremolo",
    "Vibrato",
    "Volume",
    "WebSocketClosedEvent",
)
