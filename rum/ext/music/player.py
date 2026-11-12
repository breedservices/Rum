from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import rum
from rum.voice._types import VoiceProtocol

from .enums import SearchType, TrackEndReason
from .exceptions import PlayerException
from .filters import AudioFading, Filters
from .objects import LoadResult, Track
from .queue import Queue

if TYPE_CHECKING:
    from .node import Node
    from .pool import NodePool

_log = logging.getLogger(__name__)

__all__ = ("Player",)


class Player(VoiceProtocol):
    """Voice protocol that plays audio through a Lavalink v4 or NodeLink v3 node.

    Use with ``channel.connect(cls=Player)`` (or a factory returning a configured
    player). The player attaches to ``client.music`` / ``client.lavalink``
    (:class:`~rum.ext.music.NodePool`) on connect.

    A custom queue provider can be supplied via ``queue=...`` to keep queue state
    outside RAM (e.g. disk/database-backed). The provider must implement at least
    ``loop_mode`` and ``get()`` raising :class:`~rum.ext.music.QueueEmpty`.
    """

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
        "fading",
        "filters",
        "guild",
        "guild_id",
        "node",
        "pool",
        "queue",
    )

    def __init__(
        self,
        client: rum.Client,
        channel: rum.abc.Connectable,
        *,
        queue: Any | None = None,
    ):
        """Create a player for a voice channel.

        Parameters
        ----------
        client:
            The rum client/bot instance.
        channel:
            The voice/stage channel to connect to.
        queue:
            Optional custom queue provider. Defaults to :class:`~rum.ext.music.Queue`.
        """
        super().__init__(client, channel)
        self.client: rum.Client = client
        self.channel = channel
        self.guild = getattr(channel, "guild", None)
        self.guild_id: int | None = getattr(self.guild, "id", None)

        pool = getattr(client, "music", None) or getattr(client, "lavalink", None)
        self.pool: NodePool | None = pool
        self.node: Node | None = None

        self.queue = queue if queue is not None else Queue()
        self.filters = Filters()
        self.fading: AudioFading | None = None

        self._current: Track | None = None
        self._paused = False
        self._volume = 100
        self._position = 0
        self._connected = False

        self._session_id: str | None = None
        self._voice_state: dict[str, Any] = {}
        self._voice_server: dict[str, Any] = {}

    async def on_voice_state_update(self, data) -> None:
        """Handle a Discord voice state update and forward session info to the node."""
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
                _log.exception("Failed to destroy music player for guild %s", guild_id)
            node._players.pop(guild_id, None)

    async def on_voice_server_update(self, data) -> None:
        """Handle a Discord voice server update and forward voice credentials."""
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
        """Select a node, register this player, and join the voice channel."""
        if self.pool is None:
            self.pool = getattr(self.client, "music", None) or getattr(
                self.client, "lavalink", None
            )
        if self.pool is None:
            raise PlayerException("No music NodePool attached to client (client.music)")
        if self.guild_id is None:
            raise PlayerException("Cannot determine guild id for player")

        self.node = self.pool.get_node()
        self.node._players[self.guild_id] = self
        await self.guild.change_voice_state(
            channel=self.channel, self_deaf=self_deaf, self_mute=self_mute
        )
        self._connected = True

    async def disconnect(self, *, force: bool = False) -> None:
        """Destroy the remote player and leave the voice channel."""
        self._connected = False
        guild_id = self.guild_id
        node = self.node
        try:
            if guild_id and node and node.available:
                await node.destroy_player(guild_id)
        except Exception:  # noqa: BLE001
            _log.exception("Failed to destroy music player for guild %s", guild_id)
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
        """Move the player to another voice channel."""
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
        voice: dict[str, Any] = {
            "token": token,
            "endpoint": endpoint,
            "sessionId": session_id,
        }
        channel = self.channel
        channel_id = getattr(channel, "id", None)
        if channel_id is not None:
            voice["channelId"] = str(channel_id)
        await node.update_player(guild_id, {"voice": voice})

    @property
    def current(self) -> Track | None:
        """The currently playing or last-started track, if any."""
        return self._current

    @property
    def position(self) -> int:
        """Last known playback position in milliseconds."""
        return self._position

    @property
    def paused(self) -> bool:
        """Whether playback is paused."""
        return self._paused

    @property
    def volume(self) -> int:
        """Current player volume (server-side scale, typically 0-1000)."""
        return self._volume

    @property
    def is_playing(self) -> bool:
        """Whether a track is active and not paused."""
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
        user_data: dict[str, Any] | None = None,
        audio_track_id: str | None = None,
        next_track: Track | None = None,
        fading: AudioFading | dict[str, Any] | None = None,
    ) -> Track:
        """Play or replace a track.

        Supports NodeLink/Lavalink options such as ``endTime`` (``end``),
        ``userData``, ``audioTrackId``, ``nextTrack`` preloading, and ``fading``.
        """
        node = self.node
        guild_id = self.guild_id
        if not node or not guild_id:
            raise PlayerException("Player is not connected")
        t: dict[str, Any] = {"encoded": track.encoded}
        if user_data:
            t["userData"] = user_data
        if audio_track_id:
            t["audioTrackId"] = audio_track_id
        payload: dict[str, Any] = {"track": t}
        if next_track is not None:
            payload["nextTrack"] = {"encoded": next_track.encoded}
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
        fade = fading or self.fading
        if fade is not None:
            payload["fading"] = fade.to_dict() if hasattr(fade, "to_dict") else fade
        await node.update_player(guild_id, payload, no_replace=no_replace)
        self._current = track
        return track

    async def stop(self) -> None:
        """Stop playback (sends a null track)."""
        node = self.node
        guild_id = self.guild_id
        if not node or not guild_id:
            return
        await node.update_player(guild_id, {"track": {"encoded": None}})
        self._current = None

    async def pause(self, paused: bool = True) -> None:
        """Pause or resume playback."""
        node = self.node
        guild_id = self.guild_id
        if not node or not guild_id:
            raise PlayerException("Player is not connected")
        await node.update_player(guild_id, {"paused": paused})
        self._paused = paused

    async def resume(self) -> None:
        """Resume playback."""
        await self.pause(False)

    async def seek(self, position: int) -> None:
        """Seek to ``position`` in milliseconds."""
        node = self.node
        guild_id = self.guild_id
        if not node or not guild_id:
            raise PlayerException("Player is not connected")
        pos = int(position)
        await node.update_player(guild_id, {"position": pos})
        self._position = pos

    async def set_volume(self, volume: int) -> None:
        """Set the player volume (server-side scale, typically 0-1000)."""
        node = self.node
        guild_id = self.guild_id
        if not node or not guild_id:
            raise PlayerException("Player is not connected")
        vol = int(volume)
        await node.update_player(guild_id, {"volume": vol})
        self._volume = vol

    async def set_filters(self, filters: Filters | None = None) -> None:
        """Apply current or provided filters to the player."""
        if filters is not None:
            self.filters = filters
        node = self.node
        guild_id = self.guild_id
        if not node or not guild_id:
            return
        await node.update_player(guild_id, {"filters": self.filters.to_dict()})

    async def destroy(self) -> None:
        """Alias for a forced disconnect/destroy."""
        await self.disconnect(force=True)

    async def fetch_tracks(
        self,
        query: str,
        *,
        search_type: SearchType | str | None = None,
        requester: Any = None,
    ) -> LoadResult:
        """Load tracks/playlist/search results via the node.

        If ``search_type`` is provided and ``query`` is not a URL, the appropriate
        search prefix is prepended (supports Lavalink/NodeLink prefixes).
        """
        pool = self.pool
        if pool is None:
            raise PlayerException("No music NodePool attached")
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
        """Advance the queue and play the next track.

        Respects ``queue.loop_mode == "track"`` by replaying the current track.
        Returns ``None`` when the queue is empty.
        """
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
