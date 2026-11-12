from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import rum
from rum.voice._types import VoiceProtocol

from .enums import SearchType, TrackEndReason
from .exceptions import PlayerException
from .filters import Filters
from .objects import LoadResult, Track
from .queue import Queue

if TYPE_CHECKING:
    from .node import Node
    from .pool import NodePool

_log = logging.getLogger(__name__)

__all__ = ("Player",)


class Player(VoiceProtocol):
    """A Lavalink/Nodelink-backed voice protocol for rum."""

    __slots__ = (
        "_connected",
        "_current",
        "_paused",
        "_position",
        "_session_id",
        "_voice_server",
        "_voice_state",
        "_volume",
        "channel",
        "client",
        "filters",
        "guild",
        "guild_id",
        "node",
        "pool",
        "queue",
    )

    def __init__(self, client: rum.Client, channel: rum.abc.Connectable):
        super().__init__(client, channel)
        self.client: rum.Client = client
        self.channel = channel
        self.guild = getattr(channel, "guild", None)
        self.guild_id: int | None = getattr(self.guild, "id", None)

        pool = getattr(client, "lavalink", None)
        self.pool: NodePool | None = pool
        self.node: Node | None = None

        self.queue = Queue()
        self.filters = Filters()

        self._current: Track | None = None
        self._paused = False
        self._volume = 100
        self._position = 0
        self._connected = False

        self._session_id: str | None = None
        self._voice_state: dict[str, Any] = {}
        self._voice_server: dict[str, Any] = {}

    async def on_voice_state_update(self, data) -> None:
        session_id = getattr(data, "session_id", None)
        channel_id = getattr(data, "channel_id", None)
        if hasattr(data, "get"):
            session_id = session_id or data.get("session_id")
            if channel_id is None:
                channel_id = data.get("channel_id")
        self._session_id = session_id
        self._voice_state = {"sessionId": session_id}
        if channel_id is None:
            self._connected = False
            await self._destroy_player()
            return
        await self._maybe_send_voice()

    async def _destroy_player(self) -> None:
        guild_id = self.guild_id
        node = self.node
        if guild_id and node:
            try:
                await node.destroy_player(guild_id)
            except Exception:  # noqa: BLE001
                _log.exception(
                    "Failed to destroy lavalink player for guild %s", guild_id
                )
            node._players.pop(guild_id, None)

    async def on_voice_server_update(self, data) -> None:
        token = getattr(data, "token", None)
        endpoint = getattr(data, "endpoint", None)
        guild_id = getattr(data, "guild_id", None)
        if hasattr(data, "get"):
            token = token or data.get("token")
            endpoint = endpoint if endpoint is not None else data.get("endpoint")
            guild_id = guild_id or data.get("guild_id")
        self._voice_server = {"token": token, "endpoint": endpoint}
        if guild_id and self.guild_id is None:
            self.guild_id = int(guild_id)
        await self._maybe_send_voice()

    async def connect(
        self,
        *,
        timeout: float = 30.0,
        reconnect: bool = False,
        self_deaf: bool = False,
        self_mute: bool = False,
    ) -> None:
        if self.pool is None:
            self.pool = getattr(self.client, "lavalink", None)
        if self.pool is None:
            raise PlayerException(
                "No lavalink NodePool attached to client (client.lavalink)"
            )
        if self.guild_id is None:
            raise PlayerException("Cannot determine guild id for player")

        self.node = self.pool.get_node()
        self.node._players[self.guild_id] = self
        await self.guild.change_voice_state(
            channel=self.channel, self_deaf=self_deaf, self_mute=self_mute
        )
        self._connected = True

    async def disconnect(self, *, force: bool = False) -> None:
        self._connected = False
        guild_id = self.guild_id
        node = self.node
        try:
            if guild_id and node and node.available:
                await node.destroy_player(guild_id)
        except Exception:  # noqa: BLE001
            _log.exception("Failed to destroy lavalink player for guild %s", guild_id)
        try:
            if self.guild:
                await self.guild.change_voice_state(channel=None)
        except Exception:
            if not force:
                raise
        finally:
            if guild_id and node:
                node._players.pop(guild_id, None)
            self.cleanup()

    async def move_to(self, channel: rum.abc.Connectable) -> None:
        self.channel = channel
        await self.guild.change_voice_state(channel=channel)

    async def _maybe_send_voice(self) -> None:
        session_id = self._session_id
        token = self._voice_server.get("token")
        endpoint = self._voice_server.get("endpoint")
        if not (session_id and token and endpoint):
            return
        node = self.node
        guild_id = self.guild_id
        if not node or not guild_id:
            return
        await node.update_player(
            guild_id,
            {"voice": {"token": token, "endpoint": endpoint, "sessionId": session_id}},
        )

    @property
    def current(self) -> Track | None:
        return self._current

    @property
    def position(self) -> int:
        return self._position

    @property
    def paused(self) -> bool:
        return self._paused

    @property
    def volume(self) -> int:
        return self._volume

    @property
    def is_playing(self) -> bool:
        return self._connected and self._current is not None and not self._paused

    def _update_state(self, state: dict[str, Any]) -> None:
        self._position = int(state.get("position") or 0)
        self._connected = bool(state.get("connected", self._connected))

    async def play(
        self,
        track: Track,
        *,
        start: int = 0,
        end: int | None = None,
        no_replace: bool = False,
        volume: int | None = None,
        pause: bool = False,
    ) -> Track:
        node = self.node
        guild_id = self.guild_id
        if not node or not guild_id:
            raise PlayerException("Player is not connected")
        payload: dict[str, Any] = {"track": {"encoded": track.encoded}}
        if start:
            payload["position"] = start
        if end is not None:
            payload["endTime"] = end
        if volume is not None:
            payload["volume"] = volume
            self._volume = volume
        if pause:
            payload["paused"] = True
            self._paused = True
        filters = self.filters.to_dict()
        if filters:
            payload["filters"] = filters
        await node.update_player(guild_id, payload, no_replace=no_replace)
        self._current = track
        return track

    async def stop(self) -> None:
        node = self.node
        guild_id = self.guild_id
        if not node or not guild_id:
            return
        await node.update_player(guild_id, {"track": {"encoded": None}})
        self._current = None

    async def pause(self, paused: bool = True) -> None:
        node = self.node
        guild_id = self.guild_id
        if not node or not guild_id:
            raise PlayerException("Player is not connected")
        await node.update_player(guild_id, {"paused": paused})
        self._paused = paused

    async def resume(self) -> None:
        await self.pause(False)

    async def seek(self, position: int) -> None:
        node = self.node
        guild_id = self.guild_id
        if not node or not guild_id:
            raise PlayerException("Player is not connected")
        pos = int(position)
        await node.update_player(guild_id, {"position": pos})
        self._position = pos

    async def set_volume(self, volume: int) -> None:
        node = self.node
        guild_id = self.guild_id
        if not node or not guild_id:
            raise PlayerException("Player is not connected")
        vol = int(volume)
        await node.update_player(guild_id, {"volume": vol})
        self._volume = vol

    async def set_filters(self, filters: Filters | None = None) -> None:
        if filters is not None:
            self.filters = filters
        node = self.node
        guild_id = self.guild_id
        if not node or not guild_id:
            return
        await node.update_player(guild_id, {"filters": self.filters.to_dict()})

    async def destroy(self) -> None:
        await self.disconnect(force=True)

    async def fetch_tracks(
        self,
        query: str,
        *,
        search_type: SearchType | str | None = None,
        requester: Any = None,
    ) -> LoadResult:
        pool = self.pool
        if pool is None:
            raise PlayerException("No lavalink NodePool attached")
        identifier = query
        if search_type and not query.startswith(("http://", "https://")):
            st = (
                search_type.value
                if isinstance(search_type, SearchType)
                else str(search_type)
            )
            identifier = f"{st}:{query}"
        return await pool.fetch_tracks(identifier, requester=requester, node=self.node)

    async def play_next(self) -> Track | None:
        try:
            if self.queue.loop_mode == "track" and self._current:
                return await self.play(self._current)
            track = self.queue.get()
        except Exception:  # noqa: BLE001
            self._current = None
            return None
        return await self.play(track)

    async def _on_track_end(
        self, track: Track | None, reason: TrackEndReason | str
    ) -> None:
        r = reason.value if isinstance(reason, TrackEndReason) else str(reason)
        if r in ("finished", "loadFailed"):
            try:
                await self.play_next()
            except Exception:  # noqa: BLE001
                _log.exception("Failed to advance queue for guild %s", self.guild_id)
        elif r == "stopped":
            cur = self._current
            if cur and track and cur.encoded == track.encoded:
                self._current = None
