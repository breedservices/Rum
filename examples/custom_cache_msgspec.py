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

from collections import OrderedDict
from collections.abc import Iterator, MutableMapping
from typing import Any

import msgspec

import rum


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
        self._events.append(self._encoder.encode(event))

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
        return MsgspecInstrumentedMapping("users", max_items=50_000)

    def create_guild_cache(self):
        return MsgspecInstrumentedMapping("guilds")

    def create_guild_member_cache(self, guild):
        return MsgspecInstrumentedMapping(f"guild:{getattr(guild, 'id', '?')}:members")


# Create the bot with the custom cache provider. The provider has to be
# passed when the client is constructed, so the bot is created only once.
bot = rum.Bot(cache_provider=MsgspecCacheProvider())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@bot.slash_command(description="Show custom cache stats")
async def cache_stats(ctx: rum.ApplicationContext):
    provider = ctx.bot._connection.cache_provider
    user_cache = ctx.bot._connection._users
    events = getattr(user_cache, "dump_events", lambda: [])()
    await ctx.respond(
        f"provider={type(provider).__name__} users_cached={len(user_cache)} "
        f"user_cache_events={len(events)}",
        ephemeral=True,
    )


# (Replace "token" with your bot token to run this example.)
if __name__ == "__main__":
    print("Starting bot... press Ctrl+C to stop it.")
    bot.run("MTU3MDE4NjU4MDkzNTcwNDY0Ng.G-foqs.0iSvPKYTyy3Y6hHOe3Q9hOSrAgBrG39fCSMaXk")
