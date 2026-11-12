from __future__ import annotations

from enum import Enum

__all__ = (
    "FadeCurve",
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
    TIDAL = "tdsearch"
    JIOSAAVN = "jssearch"
    YANDEX_MUSIC = "ymsearch"
    QOBUZ = "qbsearch"
    AUDIUS = "ausearch"
    VK_MUSIC = "vksearch"
    BILIBILI = "bilibili"
    GOOGLE_DRIVE = "gdsearch"
    GOOGLE_TTS = "gtts"
    FLOWERY_TTS = "ftts"


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


class FadeCurve(str, Enum):
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    S_CURVE = "s-curve"
