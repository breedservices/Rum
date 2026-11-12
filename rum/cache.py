"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-2026 Pycord Development
Copyright (c) 2026-present The rum team

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from collections import OrderedDict, deque
from collections.abc import Iterator, MutableMapping
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .message import Message
    from .state import ConnectionState
    from .ui.modal import ModalStore
    from .ui.view import ViewStore

__all__ = (
    "MessageCache",
    "CacheProvider",
    "DefaultCacheProvider",
    "LRUCache",
)


class LRUCache(MutableMapping):
    """A mapping that drops the least recently used entries beyond a limit.

    The library uses it for the caches that would otherwise grow for as long
    as the bot runs, like the user cache of a bot in many guilds.

    Parameters
    ----------
    max_entries: :class:`int`
        How many entries to keep.
    """

    __slots__ = ("_data", "max_entries")

    def __init__(self, max_entries: int) -> None:
        self.max_entries = max_entries
        self._data: OrderedDict[Any, Any] = OrderedDict()

    def __getitem__(self, key: Any) -> Any:
        value = self._data[key]
        self._data.move_to_end(key)
        return value

    def __setitem__(self, key: Any, value: Any) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        while len(self._data) > self.max_entries:
            self._data.popitem(last=False)

    def __delitem__(self, key: Any) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"<LRUCache max_entries={self.max_entries} entries={len(self)}>"


@runtime_checkable
class MessageCache(Protocol):
    """Protocol for the global message cache used by :class:`~discord.state.ConnectionState`.

    The default implementation is a :class:`collections.deque` with a ``maxlen``.
    Custom implementations should support the operations used by the library.
    """

    def append(self, message: Message, /) -> Any: ...
    def remove(self, message: Message, /) -> Any: ...
    def __iter__(self): ...
    def __reversed__(self): ...
    def __len__(self) -> int: ...
    def __bool__(self) -> bool: ...
    def clear(self) -> Any: ...


class DefaultCacheProvider:
    """Default cache backend provider.

    This provider creates the same in-memory cache objects that rum uses by
    default. Subclass this and override methods to customize specific caches.

    All mapping caches should behave like mutable mappings (``dict``-like) and
    implement at least ``__getitem__``, ``__setitem__``, ``__delitem__``,
    ``__iter__``, ``__len__``, ``get``, ``pop``, ``values``, ``items``, and
    ``__contains__`` as needed by the library.

    Parameters
    ----------
    max_messages: Optional[:class:`int`]
        Maximum number of messages to keep in the default message cache. ``None``
        disables the message cache. Defaults to ``1000`` to match library
        behavior when not specified by the client.
    max_users: Optional[:class:`int`]
        Maximum number of users to keep. The least recently used users are
        dropped beyond that. ``None`` keeps every user, which is the default.
    max_members: Optional[:class:`int`]
        Maximum number of members to keep per guild. The least recently used
        members are dropped beyond that. ``None`` keeps every member, which is
        the default.

    Attributes
    ----------
    state: Optional[:class:`~discord.state.ConnectionState`]
        The connection state the provider is attached to. The library sets this
        before it creates any cache, so implementations can use it to rebuild
        Discord objects when loading a cache from an external store.
    keeps_object_references: :class:`bool`
        Whether the caches keep a reference to the Discord objects they store.
        rum evicts a user from the user cache when the :class:`~discord.User`
        object is garbage collected. A cache that does not hold on to the
        objects, such as one backed by an external store, would lose its
        entries straight away, so set this to ``False`` for those. Defaults
        to ``True``.
    """

    def __init__(
        self,
        *,
        max_messages: int | None = 1000,
        max_users: int | None = None,
        max_members: int | None = None,
    ) -> None:
        self.max_messages = max_messages
        self.max_users = max_users
        self.max_members = max_members
        self.state: ConnectionState | None = None
        self.keeps_object_references: bool = True

    # Global/state caches

    def create_user_cache(self) -> MutableMapping[int, Any]:
        if self.max_users is None:
            return {}
        return LRUCache(self.max_users)

    def create_guild_cache(self) -> MutableMapping[int, Any]:
        return {}

    def create_emoji_cache(self) -> MutableMapping[int, Any]:
        return {}

    def create_sticker_cache(self) -> MutableMapping[int, Any]:
        return {}

    def create_poll_cache(self) -> MutableMapping[int, Any]:
        return {}

    def create_private_channel_cache(self) -> MutableMapping[int, Any]:
        return {}

    def create_private_channel_by_user_cache(self) -> MutableMapping[int, Any]:
        return {}

    def create_voice_client_cache(self) -> MutableMapping[int, Any]:
        return {}

    def create_sound_cache(self) -> MutableMapping[int, Any]:
        return {}

    # Guild-level caches

    def create_guild_channel_cache(self, guild: Any) -> MutableMapping[int, Any]:
        return {}

    def create_guild_member_cache(self, guild: Any) -> MutableMapping[int, Any]:
        if self.max_members is None:
            return {}
        return LRUCache(self.max_members)

    def create_guild_thread_cache(self, guild: Any) -> MutableMapping[int, Any]:
        return {}

    def create_guild_voice_state_cache(self, guild: Any) -> MutableMapping[int, Any]:
        return {}

    def create_guild_scheduled_event_cache(self, guild: Any) -> MutableMapping[int, Any]:
        return {}

    def create_guild_sound_cache(self, guild: Any) -> MutableMapping[int, Any]:
        return {}

    def create_guild_stage_instance_cache(self, guild: Any) -> MutableMapping[int, Any]:
        return {}

    def create_guild_role_cache(self, guild: Any) -> MutableMapping[int, Any]:
        return {}

    def create_message_cache(self) -> MessageCache | None:
        if self.max_messages is None:
            return None
        return deque(maxlen=self.max_messages)

    def clear_message_cache(self, current: MessageCache | None) -> MessageCache | None:
        """Return a cleared/reset message cache.

        Called when the state is cleared. The default implementation recreates
        the deque with the same ``maxlen``.
        """
        if self.max_messages is None or current is None:
            return None
        maxlen = getattr(current, "maxlen", self.max_messages)
        return deque(maxlen=maxlen)

    # UI stores

    def create_view_store(self, state: ConnectionState) -> ViewStore:
        from .ui.view import ViewStore

        return ViewStore(state)

    def create_modal_store(self, state: ConnectionState) -> ModalStore:
        from .ui.modal import ModalStore

        return ModalStore(state)


class CacheProvider(DefaultCacheProvider):
    """Alias for :class:`DefaultCacheProvider` for convenience."""


# Backwards-compatible alias used in some discussions/APIs.
CacheFactory = DefaultCacheProvider
