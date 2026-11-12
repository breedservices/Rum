from __future__ import annotations

__all__ = (
    "LavalinkException",
    "NoNodesAvailable",
    "NodeConnectionFailure",
    "NodeException",
    "NodeNotAvailable",
    "PlayerException",
    "QueueEmpty",
    "TrackLoadError",
)


class LavalinkException(Exception):
    """Base exception for rum.ext.lavalink."""


class NodeException(LavalinkException):
    """Base exception for node-related errors."""


class NodeConnectionFailure(NodeException):
    """Raised when a node fails to connect."""


class NodeNotAvailable(NodeException):
    """Raised when a node is not connected or not usable."""


class NoNodesAvailable(NodeException):
    """Raised when no suitable nodes are available."""


class TrackLoadError(LavalinkException):
    """Raised when loading tracks fails."""

    def __init__(
        self, message: str, severity: str | None = None, cause: str | None = None
    ):
        super().__init__(message)
        self.severity = severity
        self.cause = cause


class PlayerException(LavalinkException):
    """Raised for player-related errors."""


class QueueEmpty(PlayerException):
    """Raised when the queue is empty and an item is requested."""
