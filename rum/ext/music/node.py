from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from rum.transport import Session, WebSocket
from rum.utils import _from_json

from .enums import LoadType, ServerType
from .events import (
    ConnectionStatusEvent,
    EternalBoxInfoEvent,
    EternalBoxJumpEvent,
    FiltersChangedEvent,
    LyricsFoundEvent,
    LyricsLineEvent,
    LyricsNotFoundEvent,
    MixEndedEvent,
    MixStartedEvent,
    NodeConnectedEvent,
    NodeDisconnectedEvent,
    PauseEvent,
    PlayerConnectedEvent,
    PlayerCreatedEvent,
    PlayerDestroyedEvent,
    PlayerReconnectingEvent,
    PlayerUpdateEvent,
    RawEvent,
    SeekEvent,
    SponsorBlockSegmentSkippedEvent,
    SponsorBlockSegmentsLoadedEvent,
    StreamMetadataEvent,
    TrackEndEvent,
    TrackExceptionEvent,
    TrackStartEvent,
    TrackStuckEvent,
    VolumeChangedEvent,
    WebSocketClosedEvent,
    WorkerFailedEvent,
)
from .exceptions import NodeConnectionFailure, NodeNotAvailable, TrackLoadError
from .objects import LoadResult, Track

if TYPE_CHECKING:
    from .player import Player
    from .pool import NodePool

_log = logging.getLogger(__name__)

__all__ = ("Node",)


class Node:
    """Connection to a Lavalink v4 or NodeLink v3 server.

    Handles the WebSocket session, REST requests, and dispatching player/node
    events through :class:`~rum.ext.music.NodePool`. Select protocol behavior
    with ``server_type`` (``"lavalink"`` or ``"nodelink"``).
    """

    __slots__ = (
        "_available",
        "_own_session",
        "_players",
        "_session",
        "_session_id",
        "_ws",
        "_ws_task",
        "heartbeat",
        "host",
        "identifier",
        "password",
        "pool",
        "port",
        "resume_timeout",
        "secure",
        "server_type",
        "stats",
    )

    def __init__(
        self,
        *,
        pool: NodePool,
        host: str,
        port: int,
        password: str,
        identifier: str | None = None,
        secure: bool = False,
        server_type: ServerType | str = ServerType.LAVALINK,
        session: Session | None = None,
        heartbeat: float = 30.0,
        resume_timeout: int = 60,
    ) -> None:
        self.pool = pool
        self.host = host
        self.port = port
        self.password = password
        self.identifier = identifier or f"{host}:{port}"
        self.secure = secure
        self.server_type = (
            ServerType(server_type)
            if not isinstance(server_type, ServerType)
            else server_type
        )
        self.heartbeat = heartbeat
        self.resume_timeout = resume_timeout

        self._session = session
        self._own_session = session is None
        self._ws: WebSocket | None = None
        self._ws_task: asyncio.Task | None = None

        self._available = False
        self._session_id: str | None = None
        self._players: dict[int, Player] = {}
        self.stats: dict[str, Any] = {}

    @property
    def available(self) -> bool:
        """Whether the node's WebSocket session is connected and usable."""
        ws = self._ws
        return self._available and ws is not None and not ws.closed

    @property
    def session_id(self) -> str | None:
        """The Lavalink/NodeLink session id, once ready."""
        return self._session_id

    @property
    def players(self) -> dict[int, Player]:
        """Players registered on this node, keyed by guild id."""
        return self._players

    @property
    def player_count(self) -> int:
        """Number of players registered on this node."""
        return len(self._players)

    @property
    def is_nodelink(self) -> bool:
        """Whether this node is configured for NodeLink."""
        return self.server_type is ServerType.NODELINK

    @property
    def penalty(self) -> float:
        """Load/health penalty used for node selection (lower is better)."""
        if not self.available:
            return float("inf")
        stats = self.stats
        playing = stats.get("playingPlayers", 0) or 0
        cpu = (stats.get("cpu") or {}).get("systemLoad", 0.0) or 0.0
        frames = stats.get("frameStats") or {}
        return (
            playing
            + cpu * 100.0
            + (frames.get("nulled", 0) or 0) * 2
            + (frames.get("deficit", 0) or 0) * 2
        )

    def _base_url(self) -> str:
        return f"{'https' if self.secure else 'http'}://{self.host}:{self.port}"

    def _ws_url(self) -> str:
        return (
            f"{'wss' if self.secure else 'ws'}://{self.host}:{self.port}/v4/websocket"
        )

    def _ensure_session(self) -> Session:
        session = self._session
        if session is None:
            session = Session()
            self._session = session
            self._own_session = True
        return session

    async def connect(self) -> None:
        """Open the WebSocket connection and start listening for events."""
        self._ensure_session()
        user_id = getattr(getattr(self.pool.bot, "user", None), "id", None)
        if user_id is None:
            raise NodeConnectionFailure("Bot is not ready; user id unavailable")

        headers = {
            "Authorization": self.password,
            "User-Id": str(user_id),
            "Client-Name": f"rum-ext-music/0.1.0 ({self.server_type.value})",
        }
        if self._session_id:
            headers["Session-Id"] = self._session_id

        try:
            self._ws = await WebSocket.connect(
                self._ws_url(), headers=headers, timeout=30.0
            )
        except Exception as e:
            raise NodeConnectionFailure(
                f"Failed to connect to node {self.identifier}: {e}"
            ) from e

        self._available = True
        self._ws_task = asyncio.create_task(self._listen())
        self.pool._dispatch(NodeConnectedEvent(self))

    async def disconnect(self) -> None:
        """Close the WebSocket/session and mark the node unavailable."""
        self._available = False
        task = self._ws_task
        if task and not task.done():
            task.cancel()
            self._ws_task = None
        ws = self._ws
        if ws and not ws.closed:
            try:
                await ws.close()
            except Exception:  # noqa: BLE001, S110
                pass
        self._ws = None
        if self._own_session and self._session is not None:
            try:
                await self._session.aclose()
            except Exception:  # noqa: BLE001, S110
                pass
            self._session = None
        self.pool._dispatch(NodeDisconnectedEvent(self))

    async def _listen(self) -> None:
        ws = self._ws
        assert ws is not None
        try:
            while True:
                msg = await ws.recv()
                if msg is None:
                    break
                if isinstance(msg, bytes):
                    msg = msg.decode("utf-8", errors="replace")
                try:
                    data = _from_json(msg)
                except Exception:  # noqa: BLE001, S112
                    continue
                await self._handle_message(data)
        except asyncio.CancelledError:
            return
        except Exception:  # noqa: BLE001
            _log.exception("Error in music websocket listener for %s", self.identifier)
        finally:
            was_available = self._available
            self._available = False
            if was_available:
                self.pool._dispatch(NodeDisconnectedEvent(self))

    async def _handle_message(self, data: dict[str, Any]) -> None:
        op = data.get("op")
        if op == "ready":
            self._session_id = data.get("sessionId")
            await self._configure_session()
            return
        if op == "stats":
            self.stats = data
            return
        if op == "playerUpdate":
            player = self._players.get(int(data.get("guildId", 0)))
            if player:
                state = data.get("state") or {}
                player._update_state(state)
                self.pool._dispatch(PlayerUpdateEvent(player, self, data, state))
            return
        if op == "event":
            await self._handle_event(data)

    def _track_from(self, player: Player | None, data: dict[str, Any]) -> Track | None:
        tdata = data.get("track")
        if isinstance(tdata, dict) and tdata.get("encoded"):
            return Track.from_data(tdata)
        if player:
            return player._current
        return None

    async def _handle_event(self, data: dict[str, Any]) -> None:
        etype = data.get("type")
        guild_id = data.get("guildId")
        player = self._players.get(int(guild_id or 0)) if guild_id is not None else None

        if etype == "WorkerFailedEvent":
            self.pool._dispatch(
                WorkerFailedEvent(
                    self,
                    data.get("affectedGuilds"),
                    data.get("message"),
                    data,
                )
            )
            return
        if player is None:
            return

        track = self._track_from(player, data)

        if etype == "TrackStartEvent":
            if track:
                player._current = track
            self.pool._dispatch(
                TrackStartEvent(player, self, data, track, data.get("playingQuality"))
            )
            return
        if etype == "TrackEndEvent":
            reason = data.get("reason", "finished")
            self.pool._dispatch(TrackEndEvent(player, self, data, track, reason))
            await player._on_track_end(track, reason)
            return
        if etype == "TrackStuckEvent":
            self.pool._dispatch(
                TrackStuckEvent(
                    player,
                    self,
                    data,
                    track,
                    int(data.get("thresholdMs", 0)),
                    data.get("reason"),
                )
            )
            return
        if etype == "TrackExceptionEvent":
            self.pool._dispatch(
                TrackExceptionEvent(
                    player, self, data, track, data.get("exception") or {}
                )
            )
            return
        if etype == "WebSocketClosedEvent":
            self.pool._dispatch(
                WebSocketClosedEvent(
                    player,
                    self,
                    data,
                    int(data.get("code", 0)),
                    str(data.get("reason", "")),
                    bool(data.get("byRemote", False)),
                )
            )
            return
        if etype == "PlayerCreatedEvent":
            self.pool._dispatch(
                PlayerCreatedEvent(player, self, data, data.get("player"))
            )
            return
        if etype == "PlayerDestroyedEvent":
            self.pool._dispatch(PlayerDestroyedEvent(player, self, data))
            return
        if etype == "PlayerConnectedEvent":
            self.pool._dispatch(
                PlayerConnectedEvent(player, self, data, data.get("voice"))
            )
            return
        if etype == "PlayerReconnectingEvent":
            self.pool._dispatch(
                PlayerReconnectingEvent(player, self, data, data.get("voice"))
            )
            return
        if etype == "VolumeChangedEvent":
            vol = int(data.get("volume", 100))
            player._volume = vol
            self.pool._dispatch(VolumeChangedEvent(player, self, data, vol))
            return
        if etype == "FiltersChangedEvent":
            self.pool._dispatch(
                FiltersChangedEvent(player, self, data, data.get("filters"))
            )
            return
        if etype == "SeekEvent":
            pos = int(data.get("position", 0))
            player._position = pos
            self.pool._dispatch(SeekEvent(player, self, data, pos))
            return
        if etype == "PauseEvent":
            paused = bool(data.get("paused", False))
            player._paused = paused
            self.pool._dispatch(PauseEvent(player, self, data, paused))
            return
        if etype == "ConnectionStatusEvent":
            self.pool._dispatch(
                ConnectionStatusEvent(
                    player, self, data, data.get("status"), data.get("metrics")
                )
            )
            return
        if etype == "LyricsFoundEvent":
            self.pool._dispatch(
                LyricsFoundEvent(player, self, data, data.get("lyrics"))
            )
            return
        if etype == "LyricsLineEvent":
            self.pool._dispatch(
                LyricsLineEvent(
                    player,
                    self,
                    data,
                    int(data.get("lineIndex", 0)),
                    data.get("line"),
                )
            )
            return
        if etype == "LyricsNotFoundEvent":
            self.pool._dispatch(LyricsNotFoundEvent(player, self, data))
            return
        if etype == "MixStartedEvent":
            mix_track = None
            mt = data.get("track")
            if isinstance(mt, dict) and mt.get("encoded"):
                mix_track = Track.from_data(mt)
            self.pool._dispatch(
                MixStartedEvent(
                    player,
                    self,
                    data,
                    data.get("mixId"),
                    mix_track,
                    data.get("volume"),
                )
            )
            return
        if etype == "MixEndedEvent":
            self.pool._dispatch(
                MixEndedEvent(player, self, data, data.get("mixId"), data.get("reason"))
            )
            return
        if etype == "StreamMetadataEvent":
            self.pool._dispatch(
                StreamMetadataEvent(player, self, data, data.get("stream"))
            )
            return
        if etype == "EternalBoxInfoEvent":
            self.pool._dispatch(
                EternalBoxInfoEvent(player, self, data, data.get("eternalbox"))
            )
            return
        if etype == "EternalBoxJumpEvent":
            self.pool._dispatch(
                EternalBoxJumpEvent(
                    player,
                    self,
                    data,
                    int(data.get("fromBeat", 0)),
                    int(data.get("toBeat", 0)),
                    data.get("jumpType"),
                )
            )
            return
        if etype == "SponsorBlockSegmentsLoadedEvent":
            self.pool._dispatch(
                SponsorBlockSegmentsLoadedEvent(
                    player, self, data, data.get("segments")
                )
            )
            return
        if etype == "SponsorBlockSegmentSkippedEvent":
            self.pool._dispatch(
                SponsorBlockSegmentSkippedEvent(player, self, data, data.get("segment"))
            )
            return
        self.pool._dispatch(RawEvent(player, self, data, str(etype or "")))

    async def _configure_session(self) -> None:
        sid = self._session_id
        if not sid:
            return
        try:
            await self.request(
                "PATCH",
                f"/v4/sessions/{sid}",
                json={"resuming": True, "timeout": self.resume_timeout},
            )
        except Exception:  # noqa: BLE001
            _log.debug(
                "Failed to configure session for node %s",
                self.identifier,
                exc_info=True,
            )

    async def request(
        self, method: str, path: str, *, raw: bool = False, **kwargs: Any
    ) -> Any:
        """Perform an authenticated REST request against the node.

        Returns decoded JSON by default, ``None`` for 204, or raw ``bytes`` when
        ``raw=True``.
        """
        session = self._session
        if session is None:
            raise NodeNotAvailable(f"Node {self.identifier} has no session")
        headers = dict(kwargs.pop("headers", None) or {})
        headers["Authorization"] = self.password
        url = (
            path
            if path.startswith(("http://", "https://"))
            else self._base_url() + path
        )
        _log.debug("Music node request: %s %s", method, url)
        async with session.request(method, url, headers=headers, **kwargs) as resp:
            if resp.status == 204:
                _log.debug("Music node response: %s %s -> 204", method, url)
                return None
            body = await resp.bytes()
            if raw:
                if resp.status >= 400:
                    raise NodeNotAvailable(f"Node request failed ({resp.status})")
                _log.debug(
                    "Music node response: %s %s -> %s (%d bytes)",
                    method,
                    url,
                    resp.status,
                    len(body),
                )
                return body
            data = _from_json(body) if body else None
            _log.debug(
                "Music node response: %s %s -> %s %r", method, url, resp.status, data
            )
            if resp.status >= 400:
                raise NodeNotAvailable(f"Node request failed ({resp.status}): {data}")
            return data

    # --- Tracks / items ---

    async def get_tracks(self, identifier: str, *, requester: Any = None) -> LoadResult:
        """Resolve tracks/playlists/search results via ``/v4/loadtracks``."""
        data = await self.request(
            "GET", f"/v4/loadtracks?identifier={quote(identifier, safe='')}"
        )
        result = LoadResult.from_response(data or {}, requester=requester)
        if result.load_type == LoadType.ERROR and result.error:
            msg = result.error.get("message") or "Track load error"
            raise TrackLoadError(
                msg, result.error.get("severity"), result.error.get("cause")
            )
        return result

    async def decode_track(self, encoded: str) -> dict[str, Any]:
        return await self.request(
            "GET", f"/v4/decodetrack?encodedTrack={quote(encoded, safe='')}"
        )

    async def decode_tracks(self, encoded: list[str]) -> list[dict[str, Any]]:
        return await self.request("POST", "/v4/decodetracks", json=encoded)

    async def encode_track(self, track: dict[str, Any]) -> str:
        return await self.request("POST", "/v4/encodetrack", json=track)

    async def encode_tracks(self, tracks: list[dict[str, Any]]) -> list[str]:
        return await self.request("POST", "/v4/encodetracks", json=tracks)

    async def load_lyrics(
        self, encoded: str, *, lang: str | None = None
    ) -> dict[str, Any] | None:
        path = f"/v4/loadlyrics?encodedTrack={quote(encoded, safe='')}"
        if lang:
            path += f"&lang={quote(lang)}"
        return await self.request("GET", path)

    async def load_chapters(self, encoded: str) -> dict[str, Any] | None:
        return await self.request(
            "GET", f"/v4/loadchapters?encodedTrack={quote(encoded, safe='')}"
        )

    async def load_meaning(
        self, encoded: str, *, lang: str | None = None
    ) -> dict[str, Any] | None:
        path = f"/v4/meaning?encodedTrack={quote(encoded, safe='')}"
        if lang:
            path += f"&lang={quote(lang)}"
        return await self.request("GET", path)

    async def track_stream(self, encoded: str, *, itag: int | None = None) -> bytes:
        path = f"/v4/trackstream?encodedTrack={quote(encoded, safe='')}"
        if itag is not None:
            path += f"&itag={itag}"
        return await self.request("GET", path, raw=True)

    async def load_stream(
        self,
        encoded: str,
        *,
        volume: int | None = None,
        position: int | None = None,
        filters: dict[str, Any] | None = None,
    ) -> bytes:
        payload: dict[str, Any] = {"encodedTrack": encoded}
        if volume is not None:
            payload["volume"] = volume
        if position is not None:
            payload["position"] = position
        if filters:
            payload["filters"] = filters
        return await self.request("POST", "/v4/loadstream", json=payload, raw=True)

    # --- Players / sessions ---

    async def get_session(self, session_id: str | None = None) -> Any:
        sid = session_id or self._session_id
        if not sid:
            raise NodeNotAvailable("No session id")
        return await self.request("GET", f"/v4/sessions/{sid}")

    async def update_session(
        self, session_id: str | None = None, **payload: Any
    ) -> dict[str, Any] | None:
        sid = session_id or self._session_id
        if not sid:
            raise NodeNotAvailable("No session id")
        return await self.request("PATCH", f"/v4/sessions/{sid}", json=payload)

    async def get_players(self, session_id: str | None = None) -> Any:
        sid = session_id or self._session_id
        if not sid:
            raise NodeNotAvailable("No session id")
        return await self.request("GET", f"/v4/sessions/{sid}/players")

    async def get_player(
        self, guild_id: int, session_id: str | None = None
    ) -> dict[str, Any] | None:
        sid = session_id or self._session_id
        if not sid:
            raise NodeNotAvailable("No session id")
        return await self.request("GET", f"/v4/sessions/{sid}/players/{guild_id}")

    async def update_player(
        self, guild_id: int, payload: dict[str, Any], *, no_replace: bool = False
    ) -> dict[str, Any] | None:
        """Create or update a guild player (``PATCH /v4/sessions/{id}/players/{guild}``)."""
        sid = self._session_id
        if not sid:
            raise NodeNotAvailable(f"Node {self.identifier} has no session id yet")
        path = f"/v4/sessions/{sid}/players/{guild_id}"
        if no_replace:
            path += "?noReplace=true"
        return await self.request("PATCH", path, json=payload)

    async def destroy_player(self, guild_id: int) -> None:
        """Destroy a guild player on the node (best-effort if unavailable)."""
        sid = self._session_id
        if not sid:
            return
        try:
            await self.request("DELETE", f"/v4/sessions/{sid}/players/{guild_id}")
        except NodeNotAvailable:
            pass

    # --- Lyrics subscription (NodeLink) ---

    async def subscribe_lyrics(
        self, guild_id: int, *, skip_track_source: bool = False
    ) -> Any:
        sid = self._session_id
        if not sid:
            raise NodeNotAvailable("No session id")
        path = f"/v4/sessions/{sid}/players/{guild_id}/lyrics/subscribe"
        if skip_track_source:
            path += "?skipTrackSource=true"
        return await self.request("POST", path)

    async def unsubscribe_lyrics(self, guild_id: int) -> Any:
        sid = self._session_id
        if not sid:
            raise NodeNotAvailable("No session id")
        return await self.request(
            "DELETE", f"/v4/sessions/{sid}/players/{guild_id}/lyrics/subscribe"
        )

    # --- Mixer (NodeLink) ---

    async def add_mix(
        self, guild_id: int, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        sid = self._session_id
        if not sid:
            raise NodeNotAvailable("No session id")
        return await self.request(
            "POST", f"/v4/sessions/{sid}/players/{guild_id}/mix", json=payload
        )

    async def get_mixes(self, guild_id: int) -> Any:
        sid = self._session_id
        if not sid:
            raise NodeNotAvailable("No session id")
        return await self.request("GET", f"/v4/sessions/{sid}/players/{guild_id}/mix")

    async def update_mix(
        self, guild_id: int, mix_id: str, payload: dict[str, Any]
    ) -> Any:
        sid = self._session_id
        if not sid:
            raise NodeNotAvailable("No session id")
        return await self.request(
            "PATCH",
            f"/v4/sessions/{sid}/players/{guild_id}/mix/{mix_id}",
            json=payload,
        )

    async def remove_mix(self, guild_id: int, mix_id: str) -> Any:
        sid = self._session_id
        if not sid:
            raise NodeNotAvailable("No session id")
        return await self.request(
            "DELETE", f"/v4/sessions/{sid}/players/{guild_id}/mix/{mix_id}"
        )

    # --- SponsorBlock (NodeLink) ---

    async def get_sponsorblock(self, guild_id: int) -> Any:
        sid = self._session_id
        if not sid:
            raise NodeNotAvailable("No session id")
        return await self.request(
            "GET", f"/v4/sessions/{sid}/players/{guild_id}/sponsorblock"
        )

    async def update_sponsorblock(self, guild_id: int, payload: dict[str, Any]) -> Any:
        sid = self._session_id
        if not sid:
            raise NodeNotAvailable("No session id")
        return await self.request(
            "PATCH",
            f"/v4/sessions/{sid}/players/{guild_id}/sponsorblock",
            json=payload,
        )

    async def set_sponsorblock_segments(
        self, guild_id: int, segments: list[dict[str, Any]]
    ) -> Any:
        sid = self._session_id
        if not sid:
            raise NodeNotAvailable("No session id")
        return await self.request(
            "POST",
            f"/v4/sessions/{sid}/players/{guild_id}/sponsorblock",
            json={"segments": segments},
        )

    async def clear_sponsorblock(self, guild_id: int) -> Any:
        sid = self._session_id
        if not sid:
            raise NodeNotAvailable("No session id")
        return await self.request(
            "DELETE", f"/v4/sessions/{sid}/players/{guild_id}/sponsorblock"
        )

    # --- Node info ---

    async def get_info(self) -> Any:
        return await self.request("GET", "/v4/info")

    async def get_stats(self) -> Any:
        return await self.request("GET", "/v4/stats")

    async def get_version(self) -> Any:
        return await self.request("GET", "/version")

    async def get_routeplanner_status(self) -> Any:
        return await self.request("GET", "/v4/routeplanner/status")

    async def routeplanner_free_address(self, address: str) -> Any:
        return await self.request(
            "POST", "/v4/routeplanner/free/address", json={"address": address}
        )

    async def routeplanner_free_all(self) -> Any:
        return await self.request("POST", "/v4/routeplanner/free/all")

    async def get_youtube_config(self, *, validate: bool = False) -> Any:
        path = "/v4/youtube/config"
        if validate:
            path += "?validate=true"
        return await self.request("GET", path)

    async def update_youtube_config(self, payload: dict[str, Any]) -> Any:
        return await self.request("PATCH", "/v4/youtube/config", json=payload)

    async def youtube_oauth(self, refresh_token: str) -> Any:
        return await self.request(
            "POST", "/v4/youtube/oauth", json={"refreshToken": refresh_token}
        )

    def get_local_player(self, guild_id: int) -> Player | None:
        return self._players.get(guild_id)
