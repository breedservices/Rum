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

This example shows how to choose what the bot caches.

Every kind of thing has its own rule, set on the cache provider:

- ``enabled=False`` keeps nothing of that kind.
- ``max_entries`` keeps at most that many, dropping the least recently used.
- ``ttl`` drops an entry once it is older than that many seconds.
- ``fields`` drops every field you do not name when the entry is written.

The rules below drive the default caches (users, guilds, emojis, stickers,
channels, members and roles). The message cache is controlled by
``max_messages`` instead, and presences live on the cached members.

Set the ``BOT_TOKEN`` environment variable to run the example::

    BOT_TOKEN=your-token uv run examples/cache_rules.py
"""

import logging
import os

import rum

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger("cache_rules")

provider = rum.DefaultCacheProvider(
    # Keep no message history at all. The default is 1000 messages.
    max_messages=None,
    rules={
        # The bot never reads activities or boosts, so they are not kept.
        # Members are capped per guild; the least recently used ones go first.
        rum.CacheKind.MEMBER: rum.CacheRule(
            max_entries=5_000,
            fields=frozenset({"nick", "joined_at", "activities"}),
        ),
        # Channels are looked up by id; only names and topics are displayed.
        rum.CacheKind.CHANNEL: rum.CacheRule(
            fields=frozenset({"name", "topic"}),
        ),
        # A user that has not been seen for an hour is fetched again.
        rum.CacheKind.USER: rum.CacheRule(max_entries=20_000, ttl=3600),
        # This bot does not use custom emojis or stickers.
        rum.CacheKind.EMOJI: rum.CacheRule(enabled=False),
        rum.CacheKind.STICKER: rum.CacheRule(enabled=False),
    },
)

intents = rum.Intents.default()
intents.members = True

bot = rum.Bot(cache_provider=provider, intents=intents)


@bot.event
async def on_ready():
    logger.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    for kind, rule in provider.rules.items():
        logger.info("rule %s: %s", kind.value, rule)


@bot.slash_command(description="Show what the bot actually caches")
async def cache_stats(ctx: rum.ApplicationContext):
    connection = ctx.bot._connection
    caches = {
        "users": connection._users,
        "guilds": connection._guilds,
        "emojis": connection._emojis,
        "stickers": connection._stickers,
        "messages": connection._messages,
    }

    lines = [
        f"provider: `{type(connection.cache_provider).__name__}`",
        f"rules: {len(provider.rules)}",
    ]
    for name, cache in caches.items():
        size = len(cache) if cache is not None else 0
        lines.append(f"- {name}: {size}")

    for guild in ctx.bot.guilds[:3]:
        lines.append(
            f"- {guild.name}: {len(guild.members)} members, "
            f"{len(guild.channels)} channels, {len(guild.roles)} roles"
        )

    # The member rule drops everything it does not name, and the fields that
    # say what the object is and where it belongs are always kept.
    member = ctx.author
    if isinstance(member, rum.Member):
        lines.append(
            f"trimmed member {member.id}: nick={member.nick!r}, "
            f"activities={member.activities!r}, joined_at={member.joined_at}"
        )

    await ctx.respond("\n".join(lines), ephemeral=True)


if __name__ == "__main__":
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise SystemExit(
            "Set the BOT_TOKEN environment variable to run this example, e.g.\n"
            "    BOT_TOKEN=your-token uv run examples/cache_rules.py"
        )

    logger.info("Starting bot... press Ctrl+C to stop it.")
    bot.run(token)
