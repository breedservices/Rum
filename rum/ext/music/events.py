from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .enums import TrackEndReason
from .objects import Track

if TYPE_CHECKING:
    from .node import Node
    from .player import Player

__all__ = (
    "ConnectionStatusEvent",
    "EternalBoxInfoEvent",
    "EternalBoxJumpEvent",
    "FiltersChangedEvent",
    "LavalinkEvent",
    "LyricsFoundEvent",
    "LyricsLineEvent",
    "LyricsNotFoundEvent",
    "MixEndedEvent",
    "MixStartedEvent",
    "MusicEvent",
    "NodeConnectedEvent",
    "NodeDisconnectedEvent",
    "NodeEvent",
    "PauseEvent",
    "PlayerConnectedEvent",
    "PlayerCreatedEvent",
    "PlayerDestroyedEvent",
    "PlayerReconnectingEvent",
    "PlayerUpdateEvent",
    "RawEvent",
    "SeekEvent",
    "SponsorBlockSegmentSkippedEvent",
    "SponsorBlockSegmentsLoadedEvent",
    "StreamMetadataEvent",
    "TrackEndEvent",
    "TrackExceptionEvent",
    "TrackStartEvent",
    "TrackStuckEvent",
    "VolumeChangedEvent",
    "WebSocketClosedEvent",
    "WorkerFailedEvent",
)


@dataclass(slots=True)
class NodeEvent:
    node: Node


@dataclass(slots=True)
class NodeConnectedEvent(NodeEvent):
    pass


@dataclass(slots=True)
class NodeDisconnectedEvent(NodeEvent):
    code: int | None = None
    reason: str | None = None


@dataclass(slots=True)
class MusicEvent:
    player: Player
    node: Node
    raw: dict[str, Any] | None = None


# Backwards-compatible alias.
LavalinkEvent = MusicEvent


@dataclass(slots=True)
class TrackStartEvent(MusicEvent):
    track: Track | None = None
    playing_quality: Any = None


@dataclass(slots=True)
class TrackEndEvent(MusicEvent):
    track: Track | None = None
    reason: TrackEndReason | str = "finished"


@dataclass(slots=True)
class TrackStuckEvent(MusicEvent):
    track: Track | None = None
    threshold_ms: int = 0
    reason: str | None = None


@dataclass(slots=True)
class TrackExceptionEvent(MusicEvent):
    track: Track | None = None
    exception: dict[str, Any] | None = None


@dataclass(slots=True)
class WebSocketClosedEvent(MusicEvent):
    code: int = 0
    reason: str = ""
    by_remote: bool = False


@dataclass(slots=True)
class PlayerUpdateEvent(MusicEvent):
    state: dict[str, Any] | None = None


@dataclass(slots=True)
class PlayerCreatedEvent(MusicEvent):
    player_state: dict[str, Any] | None = None


@dataclass(slots=True)
class PlayerDestroyedEvent(MusicEvent):
    pass


@dataclass(slots=True)
class PlayerConnectedEvent(MusicEvent):
    voice: dict[str, Any] | None = None


@dataclass(slots=True)
class PlayerReconnectingEvent(MusicEvent):
    voice: dict[str, Any] | None = None


@dataclass(slots=True)
class VolumeChangedEvent(MusicEvent):
    volume: int = 100


@dataclass(slots=True)
class FiltersChangedEvent(MusicEvent):
    filters: dict[str, Any] | None = None


@dataclass(slots=True)
class SeekEvent(MusicEvent):
    position: int = 0


@dataclass(slots=True)
class PauseEvent(MusicEvent):
    paused: bool = False


@dataclass(slots=True)
class ConnectionStatusEvent(MusicEvent):
    status: str | None = None
    metrics: dict[str, Any] | None = None


@dataclass(slots=True)
class LyricsFoundEvent(MusicEvent):
    lyrics: dict[str, Any] | None = None


@dataclass(slots=True)
class LyricsLineEvent(MusicEvent):
    line_index: int = 0
    line: dict[str, Any] | None = None


@dataclass(slots=True)
class LyricsNotFoundEvent(MusicEvent):
    pass


@dataclass(slots=True)
class MixStartedEvent(MusicEvent):
    mix_id: str | None = None
    track: Track | None = None
    volume: float | None = None


@dataclass(slots=True)
class MixEndedEvent(MusicEvent):
    mix_id: str | None = None
    reason: str | None = None


@dataclass(slots=True)
class StreamMetadataEvent(MusicEvent):
    stream: dict[str, Any] | None = None


@dataclass(slots=True)
class EternalBoxInfoEvent(MusicEvent):
    eternalbox: dict[str, Any] | None = None


@dataclass(slots=True)
class EternalBoxJumpEvent(MusicEvent):
    from_beat: int = 0
    to_beat: int = 0
    jump_type: str | None = None


@dataclass(slots=True)
class SponsorBlockSegmentsLoadedEvent(MusicEvent):
    segments: list[dict[str, Any]] | None = None


@dataclass(slots=True)
class SponsorBlockSegmentSkippedEvent(MusicEvent):
    segment: dict[str, Any] | None = None


@dataclass(slots=True)
class WorkerFailedEvent(NodeEvent):
    affected_guilds: list[str] | None = None
    message: str | None = None
    raw: dict[str, Any] | None = None


@dataclass(slots=True)
class RawEvent(MusicEvent):
    type: str = ""
