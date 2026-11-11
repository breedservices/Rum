"""A pure disk backed cache for rum, using msgspec.

This example requires the 'msgspec' library::

    uv pip install msgspec

It shows how to back rum's caches with files on disk. Nothing is kept in
RAM: every entry is stored in its own JSON file and read back when it is
accessed. The files are encoded and decoded with msgspec, which is a lot
faster than the standard library's ``json`` module.

Because every lookup reads a file, this is much slower than the default
in-memory caches. It is meant as a demonstration of what the cache
provider API allows, not as a recommendation. Use SQLite or a key/value
store if you want an external cache that is actually fast.

Discord objects are not directly serialisable, they hold references to the
connection state and the guild. To persist them, each object is projected
onto the API payload shape it was built from, and rebuilt from that payload
when the file is read again. The projections below are deliberately explicit
so it is clear what is stored on disk.

The guild member cache is stored on disk, one file per member::

    rum-cache/
    └── guilds/
        └── 1548399850905665648/
            └── members/
                ├── 1490331071940657283.json
                └── ...

Set the ``BOT_TOKEN`` environment variable to run the example::

    BOT_TOKEN=your-token uv run examples/custom_cache_json_file.py
"""

import logging
import os
from collections.abc import Callable, Iterator, MutableMapping
from pathlib import Path
from typing import Any

import msgspec

import rum

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger("json_disk_cache")

#: Where the cache files are stored.
CACHE_DIRECTORY = Path(os.environ.get("RUM_CACHE_DIR", "rum-cache"))


class JsonDiskCache(MutableMapping[int, Any]):
    """A mutable mapping that stores every entry in its own JSON file.

    Nothing is kept in memory, apart from the entry ids, which are needed
    to implement ``__len__`` and ``__iter__`` without listing the directory
    on every call.

    Parameters
    ----------
    directory: :class:`pathlib.Path`
        The directory the entries are stored in.
    dump: Callable
        Turns a cached object into a JSON serialisable record.
    load: Callable
        Turns a record read back from the file into a cached object.
    """

    def __init__(
        self,
        directory: Path,
        *,
        dump: Callable[[Any], dict[str, Any]],
        load: Callable[[dict[str, Any]], Any],
    ) -> None:
        self.directory = Path(directory)
        self._dump = dump
        self._load = load
        self.directory.mkdir(parents=True, exist_ok=True)
        self._ids: set[int] | None = None

    def _path(self, key: int) -> Path:
        return self.directory / f"{key}.json"

    def _index(self) -> set[int]:
        """The ids of the cached entries, read from disk once."""
        if self._ids is None:
            self._ids = {
                int(path.stem)
                for path in self.directory.glob("*.json")
                if path.stem.isdigit()
            }
            logger.info("Found %d entries in %s", len(self._ids), self.directory)
        return self._ids

    # -- MutableMapping ------------------------------------------------

    def __getitem__(self, key: int) -> Any:
        path = self._path(key)
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            raise KeyError(key) from None

        try:
            return self._load(msgspec.json.decode(raw))
        except Exception as exc:  # a stale entry should not break the bot
            logger.warning("Could not read %s: %s", path, exc)
            raise KeyError(key) from exc

    def __setitem__(self, key: int, value: Any) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        record = self._dump(value)

        # Write to a temporary file first so a crash cannot leave a
        # half-written entry behind.
        path = self._path(key)
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_bytes(msgspec.json.encode(record))
        os.replace(temporary, path)

        self._index().add(key)

    def __delitem__(self, key: int) -> None:
        try:
            self._path(key).unlink()
        except FileNotFoundError:
            raise KeyError(key) from None
        self._index().discard(key)

    def __iter__(self) -> Iterator[int]:
        return iter(sorted(self._index()))

    def __len__(self) -> int:
        return len(self._index())

    def __repr__(self) -> str:
        return f"<JsonDiskCache {self.directory}>"


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


class JsonDiskCacheProvider(rum.DefaultCacheProvider):
    """A cache provider that stores the user and member caches on disk.

    Every other cache is kept in memory, which keeps the example short. A
    real implementation would usually want to persist more of them.
    """

    def __init__(self, directory: str | Path = CACHE_DIRECTORY) -> None:
        super().__init__()
        self.directory = Path(directory)

    def create_user_cache(self) -> MutableMapping[int, Any]:
        # The global user cache is deliberately kept in memory.
        #
        # rum evicts a user from the cache when the User object is garbage
        # collected (see User.__del__). A cache that does not hold on to the
        # objects it hands out would therefore evict every user right after
        # it was stored, which for a disk cache means deleting the file
        # again. The guild member cache below is not affected by this.
        return {}

    def create_guild_member_cache(self, guild: Any) -> MutableMapping[int, Any]:
        state = guild._state

        return JsonDiskCache(
            self.directory / "guilds" / str(guild.id) / "members",
            dump=member_to_record,
            load=lambda record: rum.Member(data=record, guild=guild, state=state),
        )


provider = JsonDiskCacheProvider()

intents = rum.Intents.default()
intents.members = True

bot = rum.Bot(cache_provider=provider, intents=intents)


@bot.event
async def on_ready():
    logger.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    logger.info("Cache directory: %s", provider.directory.resolve())
    connection = bot._connection
    logger.info("Cached users: %d", len(connection._users))
    for guild in bot.guilds:
        logger.info("Cached members for %s: %d", guild.name, len(guild._members))


@bot.slash_command(description="Show the on-disk cache directory")
async def cache_files(ctx: rum.ApplicationContext):
    root = provider.directory.resolve()
    files = list(root.rglob("*.json")) if root.exists() else []
    total = sum(path.stat().st_size for path in files)
    lines = [
        f"cache directory: `{root}`",
        f"entries on disk: {len(files)} ({total} bytes)",
    ]
    await ctx.respond("\n".join(lines), ephemeral=True)


if __name__ == "__main__":
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise SystemExit(
            "Set the BOT_TOKEN environment variable to run this example, e.g.\n"
            "    BOT_TOKEN=your-token uv run examples/custom_cache_json_file.py"
        )

    logger.info("Starting bot... press Ctrl+C to stop it.")
    bot.run(token)
