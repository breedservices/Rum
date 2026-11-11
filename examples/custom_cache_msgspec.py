# Set the BOT_TOKEN environment variable before running this example:
#     export BOT_TOKEN=your-token
# It can also be set in the .env file in the repository root.
#
# custom_cache_msgspec.py
"""This example requires the 'msgspec' library.
You can install it with: uv pip install msgspec
It demonstrates how to plug a custom cache provider into rum.
rum normally stores cached objects in RAM (dicts/deques). With a custom
cache provider you can replace those backends (e.g. bounded caches, external
stores, instrumented wrappers).
This example shows a simple instrumented mapping cache that uses msgspec to
encode lightweight cache-event records (for logging/telemetry). The Discord
objects themselves remain in memory (they are not serialized), but msgspec is
used in the cache."""

from __future__ import annotations

import logging
from collections import OrderedDict
from collections.abc import Iterator, MutableMapping
import os
from typing import Any

import msgspec

import rum

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger("cache_example")
logging.getLogger("rum").setLevel(logging.DEBUG)


class CacheEvent(msgspec.Struct):
    cache: str
    op: str
    key: int | str | None = None
    size: int | None = None


class MsgspecInstrumentedMapping(MutableMapping):
    """A dict-like cache wrapper that records operations with msgspec."""

    def __init__(self, name: str, *, max_items: int | None = None) -> None:
        self.name = name
        self.max_items = max_items
        self._data: OrderedDict[Any, Any] = OrderedDict()
        self._encoder = msgspec.json.Encoder()
        self._events: list[bytes] = []

    def _record(self, op: str, key: Any = None) -> None:
        if isinstance(key, int):
            rec_key: int | str | None = key
        elif key is None:
            rec_key = None
        else:
            rec_key = str(key)
        event = CacheEvent(cache=self.name, op=op, key=rec_key, size=len(self._data))
        # msgspec is used here to encode cache events efficiently.
        encoded = self._encoder.encode(event)
        self._events.append(encoded)
        logger.debug("cache event: %s", encoded.decode())

    def __getitem__(self, key: Any) -> Any:
        value = self._data[key]
        self._data.move_to_end(key)
        self._record("get", key)
        return value

    def __setitem__(self, key: Any, value: Any) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        if self.max_items is not None:
            while len(self._data) > self.max_items:
                evicted_key, _ = self._data.popitem(last=False)
                self._record("evict", evicted_key)
        self._record("set", key)

    def __delitem__(self, key: Any) -> None:
        del self._data[key]
        self._record("delete", key)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def get(self, key: Any, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            self._record("miss", key)
            return default

    def pop(self, key: Any, default: Any = None) -> Any:
        if key in self._data:
            value = self._data.pop(key)
            self._record("pop", key)
            return value
        self._record("miss", key)
        return default

    def clear(self) -> None:
        self._data.clear()
        self._record("clear")

    def dump_events(self) -> list[dict[str, Any]]:
        decoder = msgspec.json.Decoder()
        return [decoder.decode(raw) for raw in self._events]


class MsgspecCacheProvider(rum.DefaultCacheProvider):
    """Custom cache provider using msgspec-instrumented caches."""

    def create_user_cache(self):
        # Keep bounded in-memory user cache; events encoded with msgspec.
        logger.info("Creating user cache (max_items=50000)")
        return MsgspecInstrumentedMapping("users", max_items=50_000)

    def create_guild_cache(self):
        logger.info("Creating guild cache")
        return MsgspecInstrumentedMapping("guilds")

    def create_guild_member_cache(self, guild):
        name = f"guild:{getattr(guild, 'id', '?')}:members"
        logger.info("Creating member cache: %s", name)
        return MsgspecInstrumentedMapping(name)


# Create the bot with the custom cache provider. The provider has to be
# passed when the client is constructed, so the bot is created only once.
#
# The "members" intent is enabled so that users are actually cached. Without
# it rum replaces ``store_user`` with ``create_user`` and the user cache
# stays empty. Note that bot accounts are never cached regardless.
intents = rum.Intents.default()
intents.members = True

bot = rum.Bot(cache_provider=MsgspecCacheProvider(), intents=intents)


@bot.event
async def on_ready():
    logger.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    logger.info("------")


@bot.slash_command(description="Show custom cache stats")
async def cache_stats(ctx: rum.ApplicationContext):
    connection = ctx.bot._connection
    provider = connection.cache_provider

    caches = {
        "users": connection._users,
        "guilds": connection._guilds,
        "emojis": connection._emojis,
        "stickers": connection._stickers,
        "polls": connection._polls,
        "sounds": connection._sounds,
        "messages": connection._messages,
    }

    sizes = {name: len(cache) for name, cache in caches.items()}

    # Every cache created by the provider is an instrumented mapping, so the
    # recorded events can be decoded back into plain dictionaries.
    events = []
    for name, cache in caches.items():
        dump = getattr(cache, "dump_events", None)
        if dump is not None:
            events.extend(dump())

    logger.info(
        "cache_stats invoked by %s: provider=%s sizes=%s events=%d",
        ctx.author,
        type(provider).__name__,
        sizes,
        len(events),
    )

    lines = [f"provider: `{type(provider).__name__}`", "cache sizes:"]
    lines.extend(f"- {name}: {size}" for name, size in sizes.items())
    lines.append(f"total recorded cache events: {len(events)}")
    if events:
        lines.append("last 3 events:")
        lines.extend(f"- `{event}`" for event in events[-3:])

    await ctx.respond("\n".join(lines), ephemeral=True)


# (Replace "token" with your bot token to run this example.)
if __name__ == "__main__":
    logger.info("Starting bot... press Ctrl+C to stop it.")
    bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))