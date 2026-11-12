from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .enums import TrackEndReason
from .objects import Track

if TYPE_CHECKING:
    from .node import Node
    from .player import Player

__all__ = (
    "LavalinkEvent",
    "NodeConnectedEvent",
    "NodeDisconnectedEvent",
    "NodeEvent",
    "PlayerUpdateEvent",
    "TrackEndEvent",
    "TrackExceptionEvent",
    "TrackStartEvent",
    "TrackStuckEvent",
    "WebSocketClosedEvent",
)


@dataclass(slots=True)
class LavalinkEvent:
    player: Player
    node: Node


@dataclass(slots=True)
class TrackStartEvent(LavalinkEvent):
    track: Track | None
    raw: dict[str, Any] | None = None


@dataclass(slots=True)
class TrackEndEvent(LavalinkEvent):
    track: Track | None
    reason: TrackEndReason | str
    raw: dict[str, Any] | None = None


@dataclass(slots=True)
class TrackStuckEvent(LavalinkEvent):
    track: Track | None
    threshold_ms: int
    raw: dict[str, Any] | None = None


@dataclass(slots=True)
class TrackExceptionEvent(LavalinkEvent):
    track: Track | None
    exception: dict[str, Any]
    raw: dict[str, Any] | None = None


@dataclass(slots=True)
class WebSocketClosedEvent(LavalinkEvent):
    code: int
    reason: str
    by_remote: bool
    raw: dict[str, Any] | None = None


@dataclass(slots=True)
class PlayerUpdateEvent(LavalinkEvent):
    state: dict[str, Any]
    raw: dict[str, Any] | None = None


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
