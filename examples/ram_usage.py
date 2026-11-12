# Set the BOT_TOKEN environment variable before running this example:
#     export BOT_TOKEN=your-token
# It can also be set in the .env file in the repository root.
#
# ram_usage.py
# Shows how much memory the bot is using.
#
# Install psutil for the nicest output:
#     uv pip install psutil
#
# Without psutil the example falls back to reading /proc on Linux and to the
# standard library everywhere else.

import logging
import os
import platform
import resource
from pathlib import Path

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

    if psutil is None:
        lines.extend(
            ["", "_Install psutil for more detailed numbers._"]
        )

    return "\n".join(lines)


intents = rum.Intents.default()
bot = rum.Bot(intents=intents)


@bot.event
async def on_ready():
    logger.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    logger.info("Memory in use: %s", human_size(process_memory()["rss"]))


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


if __name__ == "__main__":
    logger.info("Starting bot... press Ctrl+C to stop it.")
    bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
