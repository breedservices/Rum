from __future__ import annotations

__all__ = (
    "LavalinkException",
    "MusicException",
    "NoNodesAvailable",
    "NodeConnectionFailure",
    "NodeException",
    "NodeNotAvailable",
    "PlayerException",
    "QueueEmpty",
    "TrackLoadError",
)


class MusicException(Exception):
    """Base exception for ``rum.ext.music``."""


# Backwards-compatible alias.
LavalinkException = MusicException


class NodeException(MusicException):
    """Base exception for node-related errors."""


class NodeConnectionFailure(NodeException):
    """Raised when a node fails to connect."""


class NodeNotAvailable(NodeException):
    """Raised when a node is not connected or not usable."""


class NoNodesAvailable(NodeException):
    """Raised when no suitable nodes are available."""


class TrackLoadError(MusicException):
    """Raised when loading tracks fails."""

    __slots__ = ("cause", "severity")

    def __init__(
        self, message: str, severity: str | None = None, cause: str | None = None
    ):
        super().__init__(message)
        self.severity = severity
        self.cause = cause


class PlayerException(MusicException):
    """Raised for player-related errors."""


class QueueEmpty(PlayerException):
    """Raised when the queue is empty and an item is requested."""
