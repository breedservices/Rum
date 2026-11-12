from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from rum.transport import Session, WebSocket
from rum.utils import _from_json

from .enums import LoadType, ServerType
from .events import (
    NodeConnectedEvent,
    NodeDisconnectedEvent,
    PlayerUpdateEvent,
    TrackEndEvent,
    TrackExceptionEvent,
    TrackStartEvent,
    TrackStuckEvent,
    WebSocketClosedEvent,
)
from .exceptions import NodeConnectionFailure, NodeNotAvailable, TrackLoadError
from .objects import LoadResult, Track

if TYPE_CHECKING:
    from .player import Player
    from .pool import NodePool

_log = logging.getLogger(__name__)

__all__ = ("Node",)


class Node:
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
        ws = self._ws
        return self._available and ws is not None and not ws.closed

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @property
    def players(self) -> dict[int, Player]:
        return self._players

    @property
    def player_count(self) -> int:
        return len(self._players)

    @property
    def is_nodelink(self) -> bool:
        return self.server_type is ServerType.NODELINK

    @property
    def penalty(self) -> float:
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
        self._ensure_session()
        user_id = getattr(getattr(self.pool.bot, "user", None), "id", None)
        if user_id is None:
            raise NodeConnectionFailure("Bot is not ready; user id unavailable")

        headers = {
            "Authorization": self.password,
            "User-Id": str(user_id),
            "Client-Name": f"rum-ext-lavalink/0.1.0 ({self.server_type.value})",
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
            _log.exception(
                "Error in lavalink websocket listener for %s", self.identifier
            )
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
        elif op == "stats":
            self.stats = data
        elif op == "playerUpdate":
            player = self._players.get(int(data.get("guildId", 0)))
            if player:
                state = data.get("state") or {}
                player._update_state(state)
                self.pool._dispatch(PlayerUpdateEvent(player, self, state, data))
        elif op == "event":
            await self._handle_event(data)

    async def _handle_event(self, data: dict[str, Any]) -> None:
        player = self._players.get(int(data.get("guildId", 0)))
        if not player:
            return
        track = player._current
        tdata = data.get("track")
        if isinstance(tdata, dict) and tdata.get("encoded"):
            track = Track.from_data(tdata)
        etype = data.get("type")
        if etype == "TrackStartEvent":
            player._current = track or player._current
            self.pool._dispatch(TrackStartEvent(player, self, track, data))
        elif etype == "TrackEndEvent":
            reason = data.get("reason", "finished")
            self.pool._dispatch(TrackEndEvent(player, self, track, reason, data))
            await player._on_track_end(track, reason)
        elif etype == "TrackStuckEvent":
            self.pool._dispatch(
                TrackStuckEvent(
                    player, self, track, int(data.get("thresholdMs", 0)), data
                )
            )
        elif etype == "TrackExceptionEvent":
            self.pool._dispatch(
                TrackExceptionEvent(
                    player, self, track, data.get("exception") or {}, data
                )
            )
        elif etype == "WebSocketClosedEvent":
            self.pool._dispatch(
                WebSocketClosedEvent(
                    player,
                    self,
                    int(data.get("code", 0)),
                    str(data.get("reason", "")),
                    bool(data.get("byRemote", False)),
                    data,
                )
            )

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

    async def request(self, method: str, path: str, **kwargs: Any) -> Any:
        session = self._session
        if session is None:
            raise NodeNotAvailable(f"Node {self.identifier} has no session")
        headers = dict(kwargs.pop("headers", None) or {})
        headers["Authorization"] = self.password
        url = self._base_url() + path
        async with session.request(method, url, headers=headers, **kwargs) as resp:
            if resp.status == 204:
                return None
            body = await resp.bytes()
            data = _from_json(body) if body else None
            if resp.status >= 400:
                raise NodeNotAvailable(f"Node request failed ({resp.status}): {data}")
            return data

    async def get_tracks(self, identifier: str, *, requester: Any = None) -> LoadResult:
        data = await self.request(
            "GET", f"/v4/loadtracks?identifier={quote(identifier)}"
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
            "GET", f"/v4/decodetrack?encodedTrack={quote(encoded)}"
        )

    async def decode_tracks(self, encoded: list[str]) -> list[dict[str, Any]]:
        return await self.request("POST", "/v4/decodetracks", json=encoded)

    async def update_player(
        self, guild_id: int, payload: dict[str, Any], *, no_replace: bool = False
    ) -> dict[str, Any] | None:
        sid = self._session_id
        if not sid:
            raise NodeNotAvailable(f"Node {self.identifier} has no session id yet")
        path = f"/v4/sessions/{sid}/players/{guild_id}"
        if no_replace:
            path += "?noReplace=true"
        return await self.request("PATCH", path, json=payload)

    async def destroy_player(self, guild_id: int) -> None:
        sid = self._session_id
        if not sid:
            return
        try:
            await self.request("DELETE", f"/v4/sessions/{sid}/players/{guild_id}")
        except NodeNotAvailable:
            pass

    def get_player(self, guild_id: int) -> Player | None:
        return self._players.get(guild_id)
