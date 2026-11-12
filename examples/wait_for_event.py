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
"""

# Set the BOT_TOKEN environment variable before running this example:
#     export BOT_TOKEN=your-token
# It can also be set in the .env file in the repository root.
#
# wait_for_event.py
import builtins
import os
import random

import rum

intents = rum.Intents.default()
intents.message_content = (
    True  # < This may give you `read-only` warning, just ignore it.
)
# This intent requires "Message Content Intent" to be enabled at https://discord.com/developers


bot = rum.Bot(intents=intents)


@bot.event
async def on_ready():
    print("Ready!")


# For more examples regarding slash commands, checkout:
# https://github.com/breedservices/Rum/tree/master/examples/app_commands


@bot.slash_command(name="guess", description="Guess a number between 1 and 10!")
async def guess_number(ctx: rum.ApplicationContext):
    await ctx.respond("Type in your number. *(It should be between 1 and 10)*")

    def is_valid_guess(m: rum.Message):
        # This function checks three things at once:
        # - The author of the message we've received via
        #   the wait_for is the same as command author.
        # - The content of the message is a digit.
        # - The digit received is within the range of 1-10.
        # If any one of these checks fail, we ignore this message.
        return (
            m.author == ctx.author and m.content.isdigit() and 1 <= int(m.content) <= 10
        )

    answer = random.randint(1, 10)

    try:
        guess: rum.Message = await bot.wait_for(
            "message", check=is_valid_guess, timeout=5.0
        )
    except builtins.TimeoutError:
        return await ctx.send_followup(f"Sorry, you took too long it was {answer}.")

    if int(guess.content) == answer:
        await guess.reply("You are right!", mention_author=True)
    else:
        await guess.reply(f"Oops. It is actually {answer}.", mention_author=True)


bot.run(os.environ.get("BOT_TOKEN", "TOKEN"))
