from __future__ import annotations

from enum import Enum

__all__ = (
    "LoadType",
    "SearchType",
    "ServerType",
    "TrackEndReason",
)


class LoadType(str, Enum):
    TRACK = "track"
    PLAYLIST = "playlist"
    SEARCH = "search"
    EMPTY = "empty"
    ERROR = "error"


class SearchType(str, Enum):
    YOUTUBE = "ytsearch"
    YOUTUBE_MUSIC = "ytmsearch"
    SOUNDCLOUD = "scsearch"
    SPOTIFY = "spsearch"
    APPLE_MUSIC = "amsearch"
    DEEZER = "dzsearch"


class ServerType(str, Enum):
    LAVALINK = "lavalink"
    NODELINK = "nodelink"


class TrackEndReason(str, Enum):
    FINISHED = "finished"
    LOAD_FAILED = "loadFailed"
    STOPPED = "stopped"
    REPLACED = "replaced"
    CLEANUP = "cleanup"

    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str):
            for member in cls:
                if member.value == value:
                    return member
        return None
