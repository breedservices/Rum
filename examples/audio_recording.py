from enum import Enum

import rum

bot = rum.Bot(debug_guilds=[...])
connections = {}


class Sinks(Enum):
    mp3 = rum.sinks.MP3Sink()
    wav = rum.sinks.WaveSink()
    pcm = rum.sinks.PCMSink()
    ogg = rum.sinks.OGGSink()
    mka = rum.sinks.MKASink()
    mkv = rum.sinks.MKVSink()
    mp4 = rum.sinks.MP4Sink()
    m4a = rum.sinks.M4ASink()


async def finished_callback(sink, channel: rum.TextChannel, *args):
    recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
    await sink.vc.disconnect()
    files = [
        rum.File(audio.file, f"{user_id}.{sink.encoding}")
        for user_id, audio in sink.audio_data.items()
    ]
    await channel.send(
        f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=files
    )


@bot.command()
async def start(ctx: rum.ApplicationContext, sink: Sinks):
    """Record your voice!"""
    voice = ctx.author.voice

    if not voice:
        return await ctx.respond("You're not in a vc right now")

    vc = await voice.channel.connect()
    connections.update({ctx.guild.id: vc})

    vc.start_recording(
        sink.value,
        finished_callback,
        ctx.channel,
    )

    await ctx.respond("The recording has started!")


@bot.command()
async def stop(ctx: rum.ApplicationContext):
    """Stop recording."""
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        vc.stop_recording()
        del connections[ctx.guild.id]
        await ctx.delete()
    else:
        await ctx.respond("Not recording in this guild.")


bot.run("TOKEN")
