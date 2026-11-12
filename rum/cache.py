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

import time
from collections import OrderedDict, deque
from collections.abc import Iterator, Mapping, MutableMapping
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .message import Message
    from .state import ConnectionState
    from .ui.modal import ModalStore
    from .ui.view import ViewStore

__all__ = (
    "MessageCache",
    "CacheKind",
    "CacheRule",
    "CacheProvider",
    "DefaultCacheProvider",
    "LRUCache",
    "NullCache",
    "trim_fields",
)


class NullCache(MutableMapping):
    """A mapping that keeps nothing, for the kinds that are not cached."""

    __slots__ = ()

    def __getitem__(self, key: Any) -> Any:
        raise KeyError(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        return None

    def __delitem__(self, key: Any) -> None:
        raise KeyError(key)

    def __iter__(self) -> Iterator[Any]:
        return iter(())

    def __len__(self) -> int:
        return 0


class CacheKind(Enum):
    """The kinds of things the cache holds.

    Every kind has its own rule, so a bot can cache the members of one guild
    and no presences at all.
    """

    CHANNEL = "channel"
    EMOJI = "emoji"
    GUILD = "guild"
    MEMBER = "member"
    MESSAGE = "message"
    PRESENCE = "presence"
    ROLE = "role"
    SCHEDULED_EVENT = "scheduled_event"
    SOUNDBOARD_SOUND = "soundboard_sound"
    STAGE_INSTANCE = "stage_instance"
    STICKER = "sticker"
    USER = "user"
    VOICE_STATE = "voice_state"


#: The fields that are always kept, because they say what an object is and
#: where it belongs.
KEPT_FIELDS = frozenset(
    {"id", "type", "guild_id", "channel_id", "user", "user_id", "guild", "owner_id"}
)


@dataclass(frozen=True)
class CacheRule:
    """How one kind of thing is cached.

    Parameters
    ----------
    enabled: :class:`bool`
        Whether the kind is cached at all.
    max_entries: :class:`int` | :obj:`None`
        How many entries are kept. The least recently used ones are dropped
        beyond that.
    ttl: :class:`float` | :obj:`None`
        How long an entry lives, in seconds. It is dropped when it is read
        after that.
    fields: :class:`frozenset`[:class:`str`] | :obj:`None`
        The fields to keep. Every other field is dropped when the entry is
        cached, so the cache only holds what the bot reads.
    """

    enabled: bool = True
    max_entries: int | None = None
    ttl: float | None = None
    fields: frozenset[str] | None = None


def trim_fields(value: Any, fields: frozenset[str]) -> None:
    """Drops every field of a cached object that the rule does not keep.

    The fields that say what an object is and where it belongs are always
    kept, and the private fields of the model are left alone.
    """
    kept = fields | KEPT_FIELDS
    for name in getattr(type(value), "__slots__", ()):
        if name.startswith("_") or name in kept:
            continue
        try:
            setattr(value, name, None)
        except AttributeError:
            pass


class LRUCache(MutableMapping):
    """A mapping that drops the least recently used entries beyond a limit.

    The library uses it for the caches that would otherwise grow for as long
    as the bot runs, like the user cache of a bot in many guilds. It also
    applies the rule of its kind: the entries expire after the time to live
    and only the fields of the rule are kept.

    Parameters
    ----------
    max_entries: :class:`int`
        How many entries to keep.
    ttl: :class:`float` | :obj:`None`
        How long an entry lives, in seconds.
    fields: :class:`frozenset`[:class:`str`] | :obj:`None`
        The fields to keep on the entries.
    """

    __slots__ = ("_data", "_stamps", "fields", "max_entries", "ttl")

    def __init__(
        self,
        max_entries: int,
        *,
        ttl: float | None = None,
        fields: frozenset[str] | None = None,
    ) -> None:
        self.max_entries = max_entries
        self.ttl = ttl
        self.fields = fields
        self._data: OrderedDict[Any, Any] = OrderedDict()
        self._stamps: dict[Any, float] = {}

    def __getitem__(self, key: Any) -> Any:
        value = self._data[key]
        if self._expired(key):
            del self._data[key]
            self._stamps.pop(key, None)
            raise KeyError(key)
        self._data.move_to_end(key)
        return value

    def __setitem__(self, key: Any, value: Any) -> None:
        if self.fields is not None:
            trim_fields(value, self.fields)
        self._data[key] = value
        self._data.move_to_end(key)
        self._stamps[key] = time.monotonic()
        while len(self._data) > self.max_entries:
            evicted, _ = self._data.popitem(last=False)
            self._stamps.pop(evicted, None)

    def __delitem__(self, key: Any) -> None:
        del self._data[key]
        self._stamps.pop(key, None)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def _expired(self, key: Any) -> bool:
        if self.ttl is None:
            return False
        stamp = self._stamps.get(key)
        if stamp is None:
            return False
        return time.monotonic() - stamp > self.ttl

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
        rules: Mapping[CacheKind, CacheRule] | None = None,
    ) -> None:
        self.max_messages = max_messages
        self.max_users = max_users
        self.max_members = max_members
        self.rules: dict[CacheKind, CacheRule] = dict(rules or {})
        self.state: ConnectionState | None = None
        self.keeps_object_references: bool = True

    def rule_for(self, kind: CacheKind) -> CacheRule:
        """Returns the rule of a kind."""
        return self.rules.get(kind, CacheRule())

    def _cache(
        self, kind: CacheKind, max_entries: int | None
    ) -> MutableMapping[Any, Any]:
        """Builds the container of a kind, with its rule applied."""
        rule = self.rule_for(kind)
        if not rule.enabled:
            return NullCache()
        if rule.max_entries is not None:
            max_entries = rule.max_entries
        if max_entries is None:
            return {}
        return LRUCache(
            max_entries,
            ttl=rule.ttl,
            fields=rule.fields,
        )

    # Global/state caches

    def create_user_cache(self) -> MutableMapping[int, Any]:
        return self._cache(CacheKind.USER, self.max_users)

    def create_guild_cache(self) -> MutableMapping[int, Any]:
        return self._cache(CacheKind.GUILD, None)

    def create_emoji_cache(self) -> MutableMapping[int, Any]:
        return self._cache(CacheKind.EMOJI, None)

    def create_sticker_cache(self) -> MutableMapping[int, Any]:
        return self._cache(CacheKind.STICKER, None)

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
        return self._cache(CacheKind.CHANNEL, None)

    def create_guild_member_cache(self, guild: Any) -> MutableMapping[int, Any]:
        return self._cache(CacheKind.MEMBER, self.max_members)

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
        return self._cache(CacheKind.ROLE, None)

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
