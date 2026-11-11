# Set the BOT_TOKEN environment variable before running this example:
#     export BOT_TOKEN=your-token
# It can also be set in the .env file in the repository root.
#
# audio_recording_merged.py
import os
import io

import pydub  # pip install pydub==0.25.1

import rum
from rum.sinks import MP3Sink

bot = rum.Bot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


async def finished_callback(sink: MP3Sink, channel: rum.TextChannel):
    mention_strs = []
    audio_segs: list[pydub.AudioSegment] = []
    files: list[rum.File] = []

    longest = pydub.AudioSegment.empty()

    for user_id, audio in sink.audio_data.items():
        mention_strs.append(f"<@{user_id}>")

        seg = pydub.AudioSegment.from_file(audio.file, format="mp3")

        # Determine the longest audio segment
        if len(seg) > len(longest):
            audio_segs.append(longest)
            longest = seg
        else:
            audio_segs.append(seg)

        audio.file.seek(0)
        files.append(rum.File(audio.file, filename=f"{user_id}.mp3"))

    for seg in audio_segs:
        longest = longest.overlay(seg)

    with io.BytesIO() as f:
        longest.export(f, format="mp3")
        await channel.send(
            f"Finished! Recorded audio for {', '.join(mention_strs)}.",
            files=files + [rum.File(f, filename="recording.mp3")],
        )


@bot.command()
async def join(ctx: rum.ApplicationContext):
    """Join the voice channel!"""
    voice = ctx.author.voice

    if not voice:
        return await ctx.respond("You're not in a vc right now")

    await voice.channel.connect()

    await ctx.respond("Joined!")


@bot.command()
async def start(ctx: rum.ApplicationContext):
    """Record the voice channel!"""
    voice = ctx.author.voice

    if not voice:
        return await ctx.respond("You're not in a vc right now")

    vc: rum.VoiceClient = ctx.voice_client

    if not vc:
        return await ctx.respond(
            "I'm not in a vc right now. Use `/join` to make me join!"
        )

    vc.start_recording(
        MP3Sink(),
        finished_callback,
        ctx.channel,
        sync_start=True,  # WARNING: This feature is very unstable and may break at any time.
    )

    await ctx.respond("The recording has started!")


@bot.command()
async def stop(ctx: rum.ApplicationContext):
    """Stop the recording"""
    vc: rum.VoiceClient = ctx.voice_client

    if not vc:
        return await ctx.respond("There's no recording going on right now")

    vc.stop_recording()

    await ctx.respond("The recording has stopped!")


@bot.command()
async def leave(ctx: rum.ApplicationContext):
    """Leave the voice channel!"""
    vc: rum.VoiceClient = ctx.voice_client

    if not vc:
        return await ctx.respond("I'm not in a vc right now")

    await vc.disconnect()

    await ctx.respond("Left!")


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
