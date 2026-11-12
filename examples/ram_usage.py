# Set the BOT_TOKEN environment variable before running this example:
#     export BOT_TOKEN=your-token
# It can also be set in the .env file in the repository root.
#
# ram_usage.py
# Shows how much memory the bot is using, while the caches are stored in a
# SQLite database instead of in memory.
#
# Install psutil for the nicest numbers:
#     uv pip install psutil
#
# Without psutil the example falls back to reading /proc on Linux and to the
# standard library everywhere else.
#
# The SQLite database is written next to the project, set RUM_CACHE_DB to
# use a different location.

import logging
import os
import platform
import resource
import sqlite3
from collections.abc import Callable, Iterator, MutableMapping
from pathlib import Path
from typing import Any

import msgspec

import rum

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger("ram_usage")

try:
    import psutil
except ImportError:
    psutil = None

#: Where the cache database is stored.
DATABASE = Path(os.environ.get("RUM_CACHE_DB", "rum-cache.sqlite3"))


def human_size(num_bytes: float) -> str:
    """Format a number of bytes in a readable way."""
    size = float(num_bytes)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(size) < 1024 or unit == "TiB":
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TiB"


def _read_proc_status() -> dict[str, int]:
    """Read the memory values of this process from /proc/self/status."""
    values: dict[str, int] = {}
    try:
        content = Path("/proc/self/status").read_text(encoding="utf-8")
    except OSError:
        return values

    for line in content.splitlines():
        key, _, rest = line.partition(":")
        if key in ("VmRSS", "VmHWM", "VmSize"):
            # The value is in kilobytes.
            values[key] = int(rest.strip().split()[0]) * 1024
    return values


def process_memory() -> dict[str, int]:
    """Return the memory usage of the bot process.

    Keys: ``rss`` (the memory currently used), ``peak`` (the highest
    amount reached) and ``virtual`` (the reserved address space).
    """
    status = _read_proc_status()

    if psutil is not None:
        info = psutil.Process().memory_info()
        rss = info.rss
        virtual = info.vms
    else:
        rss = status.get("VmRSS", 0)
        virtual = status.get("VmSize", 0)

    # psutil does not expose the peak on every platform, so it is read from
    # /proc on Linux and taken from the standard library everywhere else.
    peak = status.get("VmHWM", 0)
    if not peak:
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # Linux reports kilobytes, macOS reports bytes.
        peak = usage * 1024 if platform.system() == "Linux" else usage

    return {"rss": rss, "peak": peak, "virtual": virtual}


def system_memory() -> dict[str, int] | None:
    """Return the memory usage of the whole system, if it can be read."""
    if psutil is not None:
        virtual = psutil.virtual_memory()
        return {
            "total": virtual.total,
            "available": virtual.available,
            "used": virtual.used,
            "percent": virtual.percent,
        }

    try:
        content = Path("/proc/meminfo").read_text(encoding="utf-8")
    except OSError:
        return None

    values: dict[str, int] = {}
    for line in content.splitlines():
        key, _, rest = line.partition(":")
        if key in ("MemTotal", "MemAvailable"):
            values[key] = int(rest.strip().split()[0]) * 1024

    if "MemTotal" not in values:
        return None

    total = values["MemTotal"]
    available = values.get("MemAvailable", 0)
    used = total - available
    return {
        "total": total,
        "available": available,
        "used": used,
        "percent": int(used / total * 100) if total else 0,
    }


# -- the SQLite backed cache -------------------------------------------


class SqliteCache(MutableMapping[int, Any]):
    """A mutable mapping that stores its entries in a SQLite table.

    The keys are the snowflakes of the cached objects and the values are
    the objects, encoded as JSON with msgspec.

    Parameters
    ----------
    connection: :class:`sqlite3.Connection`
        The connection the table lives in.
    table: :class:`str`
        The name of the table the entries are stored in.
    dump: Callable
        Turns a cached object into a JSON serialisable record.
    load: Callable
        Turns a record read back from the database into a cached object.
    """

    def __init__(
        self,
        connection: sqlite3.Connection,
        table: str,
        *,
        dump: Callable[[Any], dict[str, Any]],
        load: Callable[[dict[str, Any]], Any],
    ) -> None:
        self._connection = connection
        self._table = table
        self._dump = dump
        self._load = load
        self._connection.execute(
            f'CREATE TABLE IF NOT EXISTS "{table}" '
            "(key INTEGER PRIMARY KEY, value BLOB NOT NULL)"
        )
        self._connection.commit()

    # -- MutableMapping ------------------------------------------------

    def __getitem__(self, key: int) -> Any:
        row = self._connection.execute(
            f'SELECT value FROM "{self._table}" WHERE key = ?', (key,)
        ).fetchone()
        if row is None:
            raise KeyError(key)

        try:
            return self._load(msgspec.json.decode(row[0]))
        except Exception as exc:  # a stale entry should not break the bot
            logger.warning("Could not read entry %s: %s", key, exc)
            raise KeyError(key) from exc

    def __setitem__(self, key: int, value: Any) -> None:
        blob = msgspec.json.encode(self._dump(value))
        self._connection.execute(
            f'INSERT OR REPLACE INTO "{self._table}" (key, value) VALUES (?, ?)',
            (key, blob),
        )
        self._connection.commit()

    def __delitem__(self, key: int) -> None:
        cursor = self._connection.execute(
            f'DELETE FROM "{self._table}" WHERE key = ?', (key,)
        )
        if cursor.rowcount == 0:
            raise KeyError(key)
        self._connection.commit()

    def __iter__(self) -> Iterator[int]:
        for (key,) in self._connection.execute(
            f'SELECT key FROM "{self._table}"'
        ).fetchall():
            yield int(key)

    def __len__(self) -> int:
        row = self._connection.execute(
            f'SELECT COUNT(*) FROM "{self._table}"'
        ).fetchone()
        return int(row[0]) if row else 0

    def __repr__(self) -> str:
        return f"<SqliteCache {self._table} entries={len(self)}>"


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


class SqliteCacheProvider(rum.DefaultCacheProvider):
    """A cache provider that stores the caches in a SQLite database.

    The database is opened in WAL mode so that reads do not block writes,
    which keeps the bot responsive while the caches are being filled.
    """

    def __init__(self, database: str | Path = DATABASE) -> None:
        super().__init__()
        self.database = Path(database)
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.database, check_same_thread=False)
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._connection.execute("PRAGMA synchronous = NORMAL")
        # The caches do not keep the Discord objects alive, so rum must not
        # evict the user cache when a User object is garbage collected.
        self.keeps_object_references = False

    def create_user_cache(self) -> MutableMapping[int, Any]:
        state = self.state
        if state is None:  # pragma: no cover - the library always sets this
            return {}

        return SqliteCache(
            self._connection,
            "users",
            dump=user_to_record,
            load=lambda record: rum.User(state=state, data=record),
        )

    def create_guild_member_cache(self, guild: Any) -> MutableMapping[int, Any]:
        state = guild._state

        return SqliteCache(
            self._connection,
            f"guild_{guild.id}_members",
            dump=member_to_record,
            load=lambda record: rum.Member(data=record, guild=guild, state=state),
        )

    def table_sizes(self) -> dict[str, int]:
        """The number of entries in every table of the database."""
        sizes: dict[str, int] = {}
        for (table,) in self._connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall():
            row = self._connection.execute(
                f'SELECT COUNT(*) FROM "{table}"'
            ).fetchone()
            sizes[table] = int(row[0]) if row else 0
        return sizes


provider = SqliteCacheProvider()


def format_report() -> str:
    """Build a human readable memory report."""
    process = process_memory()
    lines = [
        "**Bot process**",
        f"- memory in use: {human_size(process['rss'])}",
        f"- peak memory: {human_size(process['peak'])}",
    ]
    if process["virtual"]:
        lines.append(f"- reserved address space: {human_size(process['virtual'])}")

    system = system_memory()
    if system is not None:
        lines.extend(
            [
                "",
                "**System**",
                f"- total: {human_size(system['total'])}",
                f"- in use: {human_size(system['used'])} ({system['percent']}%)",
                f"- available: {human_size(system['available'])}",
            ]
        )
    else:
        lines.extend(["", "_System memory is not available on this platform._"])

    lines.extend(["", "**Cache (SQLite)**"])
    try:
        size = provider.database.stat().st_size
        lines.append(f"- database: `{provider.database}` ({human_size(size)})")
        for table, count in provider.table_sizes().items():
            lines.append(f"- {table}: {count} entries")
    except OSError as exc:
        lines.append(f"- could not read the database: {exc}")

    if psutil is None:
        lines.extend(["", "_Install psutil for more detailed numbers._"])

    return "\n".join(lines)


intents = rum.Intents.default()
intents.members = True

bot = rum.Bot(cache_provider=provider, intents=intents)


@bot.event
async def on_ready():
    logger.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    logger.info("Memory in use: %s", human_size(process_memory()["rss"]))
    logger.info("Cache database: %s", provider.database.resolve())


@bot.slash_command(description="Show the memory usage of the bot and the system")
async def ram(ctx: rum.ApplicationContext):
    report = format_report()
    logger.info("Memory report:\n%s", report)
    await ctx.respond(report, ephemeral=True)


@bot.slash_command(description="Show just the memory the bot is using")
async def ram_process(ctx: rum.ApplicationContext):
    process = process_memory()
    await ctx.respond(
        f"Using **{human_size(process['rss'])}** "
        f"(peak {human_size(process['peak'])})",
        ephemeral=True,
    )


@bot.slash_command(description="Show what is stored in the cache database")
async def cache(ctx: rum.ApplicationContext):
    lines = [f"database: `{provider.database.resolve()}`"]
    for table, count in provider.table_sizes().items():
        lines.append(f"- {table}: {count} entries")
    await ctx.respond("\n".join(lines), ephemeral=True)


if __name__ == "__main__":
    logger.info("Starting bot... press Ctrl+C to stop it.")
    bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
