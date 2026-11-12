from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any, ClassVar

from .enums import ServerType
from .exceptions import NodeException, NoNodesAvailable
from .node import Node
from .objects import LoadResult

if TYPE_CHECKING:
    import rum
    from rum.transport import Session

    from .events import MusicEvent, NodeEvent

_log = logging.getLogger(__name__)

__all__ = ("NodePool",)

_CAMEL_RE = re.compile(r"(?<!^)(?=[A-Z])")


class NodePool:
    """Manages music nodes for a bot and dispatches music events.

    A pool is attached to the bot as ``bot.music`` (and ``bot.lavalink`` for
    compatibility). Events are dispatched as ``on_music_*`` handlers.
    """

    __slots__ = ("_nodes", "bot")
    _pools: ClassVar[dict[int, NodePool]] = {}

    def __init__(self, bot: rum.Client) -> None:
        """Create and attach a node pool to ``bot``."""
        self.bot = bot
        self._nodes: dict[str, Node] = {}
        self._pools[id(bot)] = self
        bot.music = self
        bot.lavalink = self

    @property
    def nodes(self) -> dict[str, Node]:
        """A snapshot mapping of node identifiers to nodes."""
        return dict(self._nodes)

    @classmethod
    def get_pool(cls, bot: rum.Client) -> NodePool | None:
        """Return the pool attached to ``bot``, if any."""
        pool = cls._pools.get(id(bot))
        if pool is None:
            pool = getattr(bot, "music", None) or getattr(bot, "lavalink", None)
        return pool

    @classmethod
    async def create_node(
        cls,
        *,
        bot: rum.Client,
        host: str,
        port: int,
        password: str,
        identifier: str | None = None,
        secure: bool = False,
        server_type: ServerType | str = ServerType.LAVALINK,
        session: Session | None = None,
        heartbeat: float = 30.0,
        resume_timeout: int = 60,
    ) -> Node:
        """Create (or reuse) the bot's pool, add a node, and connect it.

        Set ``server_type`` to ``"lavalink"`` or ``"nodelink"`` to match the server.
        """
        pool = cls.get_pool(bot) or cls(bot)
        return await pool.add_node(
            host=host,
            port=port,
            password=password,
            identifier=identifier,
            secure=secure,
            server_type=server_type,
            session=session,
            heartbeat=heartbeat,
            resume_timeout=resume_timeout,
        )

    async def add_node(
        self,
        *,
        host: str,
        port: int,
        password: str,
        identifier: str | None = None,
        secure: bool = False,
        server_type: ServerType | str = ServerType.LAVALINK,
        session: Session | None = None,
        heartbeat: float = 30.0,
        resume_timeout: int = 60,
    ) -> Node:
        """Add and connect a node to this pool."""
        node = Node(
            pool=self,
            host=host,
            port=port,
            password=password,
            identifier=identifier,
            secure=secure,
            server_type=server_type,
            session=session,
            heartbeat=heartbeat,
            resume_timeout=resume_timeout,
        )
        if node.identifier in self._nodes:
            raise NodeException(
                f"Node with identifier {node.identifier!r} already exists"
            )
        self._nodes[node.identifier] = node
        await node.connect()
        return node

    def get_node(self, *, identifier: str | None = None) -> Node:
        """Return a specific node or the best available node by penalty."""
        if identifier:
            node = self._nodes.get(identifier)
            if not node or not node.available:
                raise NoNodesAvailable(f"Node {identifier!r} is not available")
            return node
        best = None
        best_penalty = float("inf")
        for n in self._nodes.values():
            if not n.available:
                continue
            p = n.penalty
            if p < best_penalty:
                best_penalty = p
                best = n
        if best is None:
            raise NoNodesAvailable("No available music nodes")
        return best

    async def fetch_tracks(
        self, query: str, *, requester: Any = None, node: Node | None = None
    ) -> LoadResult:
        """Load tracks via the given or best available node."""
        if node is None:
            node = self.get_node()
        return await node.get_tracks(query, requester=requester)

    def _dispatch(self, event: MusicEvent | NodeEvent) -> None:
        name = type(event).__name__
        snake = _CAMEL_RE.sub("_", name).lower()
        snake = snake.removesuffix("_event")
        try:
            self.bot.dispatch(f"music_{snake}", event)
        except Exception:  # noqa: BLE001
            _log.exception("Error dispatching music_%s", snake)

    async def disconnect(self) -> None:
        """Disconnect and remove all nodes from the pool."""
        for node in list(self._nodes.values()):
            try:
                await node.disconnect()
            except Exception:  # noqa: BLE001
                _log.exception("Error disconnecting node %s", node.identifier)
        self._nodes.clear()
        self._pools.pop(id(self.bot), None)
