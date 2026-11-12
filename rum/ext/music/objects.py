from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import LoadType

__all__ = ("LoadResult", "Playlist", "Track")


@dataclass(slots=True)
class Track:
    """A playable track returned by a Lavalink or NodeLink node.

    Stores the encoded track and commonly used metadata. ``plugin_info``,
    ``user_data``, and ``extras`` preserve additional payload fields when present.
    """

    encoded: str
    identifier: str = ""
    title: str = "Unknown title"
    author: str = "Unknown author"
    uri: str | None = None
    source_name: str | None = None
    duration: int = 0
    position: int = 0
    is_stream: bool = False
    is_seekable: bool = True
    artwork_url: str | None = None
    isrc: str | None = None
    requester: Any = None
    plugin_info: dict[str, Any] | None = None
    user_data: dict[str, Any] | None = None
    extras: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_data(cls, data: dict[str, Any], *, requester: Any = None) -> Track:
        info = data.get("info") or {}
        extras = {}
        for k, v in data.items():
            if k not in ("encoded", "track", "info", "pluginInfo", "userData"):
                extras[k] = v
        return cls(
            encoded=data.get("encoded") or data.get("track") or "",
            identifier=info.get("identifier") or "",
            title=info.get("title") or "Unknown title",
            author=info.get("author") or "Unknown author",
            uri=info.get("uri"),
            source_name=info.get("sourceName"),
            duration=int(info.get("length") or 0),
            position=int(info.get("position") or 0),
            is_stream=bool(info.get("isStream")),
            is_seekable=bool(info.get("isSeekable", True)),
            artwork_url=info.get("artworkUrl"),
            isrc=info.get("isrc"),
            requester=requester,
            plugin_info=data.get("pluginInfo") or None,
            user_data=data.get("userData") or None,
            extras=extras,
        )

    @property
    def length(self) -> int:
        return self.duration

    def __str__(self) -> str:
        return self.title


@dataclass(slots=True)
class Playlist:
    """A playlist returned by a Lavalink or NodeLink node."""

    name: str
    tracks: list[Track]
    selected_track: int = -1
    info: dict[str, Any] = field(default_factory=dict)
    requester: Any = None

    @classmethod
    def from_data(cls, data: dict[str, Any], *, requester: Any = None) -> Playlist:
        playlist_info = data.get("info") or {}
        tracks = [
            Track.from_data(t, requester=requester) for t in (data.get("tracks") or [])
        ]
        return cls(
            name=playlist_info.get("name") or "Unknown playlist",
            tracks=tracks,
            selected_track=int(playlist_info.get("selectedTrack", -1)),
            info=playlist_info,
            requester=requester,
        )


@dataclass(slots=True)
class LoadResult:
    """Result of a track/playlist/search load request."""

    load_type: LoadType
    tracks: list[Track] = field(default_factory=list)
    playlist: Playlist | None = None
    error: dict[str, Any] | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_response(
        cls, data: dict[str, Any], *, requester: Any = None
    ) -> LoadResult:
        load_type = LoadType(data.get("loadType", "empty"))
        payload = data.get("data")
        tracks: list[Track] = []
        playlist: Playlist | None = None
        error: dict[str, Any] | None = None

        if load_type == LoadType.TRACK and payload:
            tracks = [Track.from_data(payload, requester=requester)]
        elif load_type == LoadType.SEARCH and isinstance(payload, list):
            tracks = [Track.from_data(t, requester=requester) for t in payload]
        elif load_type == LoadType.PLAYLIST and payload:
            playlist = Playlist.from_data(payload, requester=requester)
            tracks = list(playlist.tracks)
        elif load_type == LoadType.ERROR and isinstance(payload, dict):
            error = payload

        return cls(
            load_type=load_type, tracks=tracks, playlist=playlist, error=error, raw=data
        )
