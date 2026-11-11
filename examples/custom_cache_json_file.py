"""A JSON file backed cache for rum, using msgspec.

This example requires the 'msgspec' library::

    uv pip install msgspec

It shows how to back rum's caches with files on disk instead of RAM. The
caches are written as JSON with msgspec, which is a lot faster than the
standard library's ``json`` module, and are read back when the bot starts.

Discord objects are not directly serialisable, they hold references to the
connection state and the guild. To persist them, each object is projected
onto the API payload shape it was built from, and rebuilt from that payload
when the file is read again. The projections below are deliberately explicit
so it is clear what is stored on disk.

The files are written to a directory (``rum-cache`` by default) and are
updated at most once every few seconds, plus once when the bot stops.
"""

from __future__ import annotations

import atexit
import logging
import os
import time
from collections.abc import Callable, Iterator, MutableMapping
from pathlib import Path
from typing import Any

import msgspec

import rum

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger("json_file_cache")

#: How long to wait before writing a cache back to disk.
FLUSH_INTERVAL = 5.0


class JsonFileCache(MutableMapping[int, Any]):
    """A mutable mapping that persists its entries to a JSON file.

    Parameters
    ----------
    path: :class:`pathlib.Path`
        The file the cache is stored in.
    dump: Callable
        Turns a cached object into a JSON serialisable record.
    load: Callable
        Turns a record read back from the file into a cached object.
    """

    def __init__(
        self,
        path: Path,
        *,
        dump: Callable[[Any], dict[str, Any]],
        load: Callable[[dict[str, Any]], Any],
    ) -> None:
        self.path = path
        self._dump = dump
        self._load = load
        self._data: dict[int, Any] = {}
        self._dirty = False
        self._last_flush = 0.0
        self._read()

    # -- persistence ---------------------------------------------------

    def _read(self) -> None:
        """Load the cache from disk, ignoring anything that cannot be read."""
        try:
            raw = self.path.read_bytes()
        except OSError:
            return

        if not raw:
            return

        try:
            records = msgspec.json.decode(raw)
        except msgspec.DecodeError as exc:
            logger.warning("Could not decode %s: %s", self.path, exc)
            return

        for key, record in records.items():
            try:
                self._data[int(key)] = self._load(record)
            except Exception as exc:  # a stale entry should not break the bot
                logger.warning("Skipping cached entry %s: %s", key, exc)

        logger.info("Loaded %d entries from %s", len(self._data), self.path)

    def _write(self) -> None:
        """Write the cache to disk."""
        records = {str(key): self._dump(value) for key, value in self._data.items()}

        # Write to a temporary file first so a crash cannot leave a
        # half-written cache behind.
        temporary = self.path.with_name(self.path.name + ".tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary.write_bytes(msgspec.json.encode(records))
            os.replace(temporary, self.path)
        except OSError as exc:
            logger.warning("Could not write %s: %s", self.path, exc)
            return

        logger.info("Wrote %d entries to %s", len(records), self.path)

    def flush(self) -> None:
        """Write the cache to disk if it changed."""
        if self._dirty:
            self._dirty = False
            self._last_flush = time.monotonic()
            self._write()

    def _touch(self) -> None:
        """Mark the cache as changed and write it out eventually."""
        self._dirty = True
        if time.monotonic() - self._last_flush >= FLUSH_INTERVAL:
            self.flush()

    # -- MutableMapping ------------------------------------------------

    def __getitem__(self, key: int) -> Any:
        return self._data[key]

    def __setitem__(self, key: int, value: Any) -> None:
        self._data[key] = value
        self._touch()

    def __delitem__(self, key: int) -> None:
        del self._data[key]
        self._touch()

    def __iter__(self) -> Iterator[int]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"<JsonFileCache {self.path.name} entries={len(self._data)}>"


# -- projections -------------------------------------------------------
#
# Discord objects are not JSON serialisable, so they are projected onto the
# payload shape they were created from.


def user_to_record(user: rum.User) -> dict[str, Any]:
    """Project a user onto the API payload shape."""
    return {
        "id": user.id,
        "username": user.name,
        "discriminator": user.discriminator,
        "global_name": user.global_name,
        "avatar": user._avatar,
        "banner": user._banner,
        "bot": user.bot,
        "public_flags": user._public_flags,
    }


def member_to_record(member: rum.Member) -> dict[str, Any]:
    """Project a member onto the API payload shape."""
    return {
        "user": user_to_record(member._user),
        "roles": list(member._roles),
        "nick": member.nick,
        "pending": member.pending,
        "avatar": member._avatar,
        "banner": member._banner,
        "flags": member.flags.value,
        "joined_at": member.joined_at.isoformat() if member.joined_at else None,
        "premium_since": (
            member.premium_since.isoformat() if member.premium_since else None
        ),
    }


class JsonFileCacheProvider(rum.DefaultCacheProvider):
    """A cache provider that stores the user and member caches on disk.

    Every other cache is kept in memory, which keeps the example short. A
    real implementation would usually want to persist more of them.
    """

    def __init__(self, directory: str | Path = "rum-cache") -> None:
        super().__init__()
        self.directory = Path(directory)
        self._caches: list[JsonFileCache] = []

    def _cache(self, name: str, **kwargs: Any) -> JsonFileCache:
        cache = JsonFileCache(self.directory / f"{name}.json", **kwargs)
        self._caches.append(cache)
        return cache

    def create_user_cache(self) -> MutableMapping[int, Any]:
        state = self.state
        if state is None:  # pragma: no cover - the library always sets this
            return {}

        return self._cache(
            "users",
            dump=user_to_record,
            load=lambda record: rum.User(state=state, data=record),
        )

    def create_guild_member_cache(self, guild: Any) -> MutableMapping[int, Any]:
        state = guild._state
        guild_id = guild.id

        return self._cache(
            f"guild_{guild_id}_members",
            dump=member_to_record,
            load=lambda record: rum.Member(
                data=record, guild=guild, state=state
            ),
        )

    def flush(self) -> None:
        """Write every cache to disk."""
        for cache in self._caches:
            cache.flush()


provider = JsonFileCacheProvider()


@atexit.register
def _flush_on_exit() -> None:
    provider.flush()


intents = rum.Intents.default()
intents.members = True

bot = rum.Bot(cache_provider=provider, intents=intents)


@bot.event
async def on_ready():
    logger.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    connection = bot._connection
    logger.info("Restored %d users from disk", len(connection._users))
    for guild in bot.guilds:
        logger.info(
            "Restored %d members for guild %s", len(guild._members), guild.name
        )


@bot.slash_command(description="Show the on-disk cache files")
async def cache_files(ctx: rum.ApplicationContext):
    files = sorted(provider.directory.glob("*.json"))
    lines = [f"cache directory: `{provider.directory}`"]
    for path in files:
        size = path.stat().st_size
        lines.append(f"- `{path.name}` ({size} bytes)")
    await ctx.respond("\n".join(lines) or "no cache files yet", ephemeral=True)


if __name__ == "__main__":
    logger.info("Starting bot... press Ctrl+C to stop it.")
    bot.run("TOKEN")
