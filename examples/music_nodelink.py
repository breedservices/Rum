"""Basic music bot example using rum.ext.music with a NodeLink v3 server.

Set BOT_TOKEN and ensure a NodeLink v3 node is running and reachable.
Configure with NODELINK_URI/NODELINK_PASSWORD (or node_uri/node_password), or
with NODELINK_HOST/NODELINK_PORT/NODELINK_SECURE/NODELINK_PASSWORD.
"""

import logging
import os
from urllib.parse import urlparse

import rum
from rum.ext import commands
from rum.ext.music import NodePool, Player, SearchType, ServerType, TrackEndEvent

logging.basicConfig(level=logging.INFO)
logging.getLogger("rum.ext.music").setLevel(logging.DEBUG)


def _load_nodelink_config() -> tuple[str, int, str, bool]:
    uri = os.getenv("NODELINK_URI") or os.getenv("node_uri")
    password = (
        os.getenv("NODELINK_PASSWORD")
        or os.getenv("node_password")
        or "youshallnotpass"
    )
    if uri:
        parsed = urlparse(uri)
        secure = parsed.scheme in ("https", "wss")
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if secure else 2333)
        return host, port, password, secure
    host = os.getenv("NODELINK_HOST", "localhost")
    port = int(os.getenv("NODELINK_PORT", "2333"))
    secure = os.getenv("NODELINK_SECURE", "").lower() in ("1", "true", "yes")
    return host, port, password, secure


NODELINK_HOST, NODELINK_PORT, NODELINK_PASSWORD, NODELINK_SECURE = (
    _load_nodelink_config()
)

intents = rum.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await NodePool.create_node(
        bot=bot,
        host=NODELINK_HOST,
        port=NODELINK_PORT,
        password=NODELINK_PASSWORD,
        secure=NODELINK_SECURE,
        server_type=ServerType.NODELINK,
    )
    print("Connected to NodeLink node")


@bot.listen("on_music_track_end")
async def on_music_track_end(event: TrackEndEvent):
    if event.reason == "finished":
        await event.player.play_next()


@bot.command()
async def join(ctx: commands.Context):
    """Join the author's voice channel."""
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("Join a voice channel first.")
        return
    if ctx.voice_client:
        await ctx.voice_client.move_to(ctx.author.voice.channel)
    else:
        await ctx.author.voice.channel.connect(cls=Player)
    await ctx.send("Joined.")


@bot.command()
async def play(ctx: commands.Context, *, query: str):
    """Search and play/add a track through NodeLink."""
    player = ctx.voice_client
    if not player:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("Join a voice channel first.")
            return
        player = await ctx.author.voice.channel.connect(cls=Player)

    result = await player.fetch_tracks(query, search_type=SearchType.YOUTUBE)
    if not result.tracks:
        await ctx.send("No tracks found.")
        return

    track = result.tracks[0]
    track.requester = ctx.author
    if player.is_playing:
        player.queue.add(track)
        await ctx.send(f"Queued: {track.title}")
    else:
        await player.play(track)
        await ctx.send(f"Now playing: {track.title}")


@bot.command()
async def skip(ctx: commands.Context):
    """Skip the current track."""
    player = ctx.voice_client
    if not player or not player.current:
        await ctx.send("Nothing is playing.")
        return
    await player.stop()
    await ctx.send("Skipped.")


@bot.command()
async def stop(ctx: commands.Context):
    """Stop playback and clear the queue."""
    player = ctx.voice_client
    if not player:
        await ctx.send("Not connected.")
        return
    player.queue.clear()
    await player.stop()
    await ctx.send("Stopped.")


@bot.command()
async def disconnect(ctx: commands.Context):
    """Disconnect from voice."""
    player = ctx.voice_client
    if player:
        await player.disconnect()
        await ctx.send("Disconnected.")
    else:
        await ctx.send("Not connected.")


token = os.environ.get("BOT_TOKEN")
if not token:
    raise RuntimeError(
        "Set the BOT_TOKEN environment variable (or put it in .env) before running this example."
    )
bot.run(token)
