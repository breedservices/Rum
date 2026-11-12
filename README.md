<!-- readme-metadata
description: rum - a Discord API wrapper for Python, forked from Pycord
keywords: discord, discord-bot, python, async, pycord, rum, bot, api-wrapper
homepage: https://github.com/breedservices/Rum
-->

# rum

This is the **rum** Discord library — a fork of [Pycord](https://github.com/Pycord-Development/pycord).

rum is an async Python API wrapper for the Discord API, based on Pycord. It keeps the familiar API style while evolving independently.

## Documentation

The documentation lives in [`docs/`](./docs) and renders directly on GitHub, so there
is no site to build:

- [Guides](./docs/index.mdx) — installing, quickstart, intents, cogs, FAQ and the
  `ext` command framework
- [API reference](./docs/api/index.mdx) — one page per module, generated from the
  docstrings
- [`examples/`](./examples) — runnable bots, including cache providers and cache rules

The API reference is generated. After changing a docstring, regenerate it:

```sh
uv run --with pypandoc-binary python docs/generate_reference.py
```

[Pycord's documentation](https://docs.pycord.dev) is still useful for concepts that
carry over unchanged.

## Installation

rum is not published on PyPI. Install it directly from the repository URL:

```sh
# pip
pip install git+https://github.com/breedservices/Rum.git

# or with extras
pip install "rum[voice] @ git+https://github.com/breedservices/Rum.git"
pip install "rum[music] @ git+https://github.com/breedservices/Rum.git"
```

Python 3.11+ is required.

## Quick Example

```py
import rum

intents = rum.Intents.default()

bot = rum.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run("TOKEN")
```

rum is the actual library. If you prefer compatibility-style imports, `import discord`
also works and resolves to the very same modules.

## Caching

Anything rum keeps in RAM can be swapped out through a **cache provider**. Pass one
to the client and it is used for every cache the library creates:

```py
import rum

bot = rum.Bot(cache_provider=MyProvider())
```

See the examples for working implementations:

- [`examples/custom_cache_msgspec.py`](./examples/custom_cache_msgspec.py) — an
  instrumented in-memory cache that encodes cache events with `msgspec`
- [`examples/custom_cache_json_file.py`](./examples/custom_cache_json_file.py) — a
  pure disk cache that stores every entry in its own JSON file
- [`examples/ram_usage.py`](./examples/ram_usage.py) — a bot that keeps its caches
  in a SQLite database and reports how much memory it is using
- [`examples/cache_rules.py`](./examples/cache_rules.py) — per-kind cache rules, so
  one guild's members can be cached while presences are not, with TTLs and size caps

## Music (Lavalink / NodeLink)

`rum.ext.music` provides a low-RAM client for **Lavalink v4** and **NodeLink v3**
over rum's transport (no `aiohttp`). Choose the server protocol at node creation
with `server_type="lavalink"` or `server_type="nodelink"`.

```py
from rum.ext.music import NodePool, ServerType

await NodePool.create_node(
    bot=bot,
    host="localhost",
    port=2333,
    password="youshallnotpass",
    server_type=ServerType.LAVALINK,  # or ServerType.NODELINK
)
```

Examples:

- [`examples/music_lavalink.py`](./examples/music_lavalink.py) — Lavalink v4
- [`examples/music_nodelink.py`](./examples/music_nodelink.py) — NodeLink v3

All examples read the bot token from the `BOT_TOKEN` environment variable, or
from the `.env` file in the repository root:

```sh
export BOT_TOKEN=your-token          # or put it in .env
uv run examples/basic_bot.py
```

## Logging

rum uses the standard [`logging`](https://docs.python.org/3/library/logging.html)
module. The library loggers are named `rum` and its submodules, e.g. `rum.client`,
`rum.gateway` and `rum.http`.

The quickest way to see what the library is doing:

```py
import logging

import rum

rum.utils.setup_logging(level=logging.DEBUG)
```

Or configure it yourself:

```py
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and builds.

```sh
# Create the environment and install the dev/test dependencies
uv sync --group dev --group test --extra voice

# Run the tests
uv run pytest

# Build the sdist and wheel
uv build
```

Extras are selected with `--extra`, e.g. `uv sync --extra voice`.

If you prefer pip, quote extras in `zsh` to avoid glob expansion, for example:

```sh
uv pip install -e ".[voice]"
```

The project metadata (summary and keywords) is derived from this file's
`readme-metadata` block by `scripts/readme_metadata.py`, so the README stays the
single source of truth. A CI job verifies the built package matches it.

## License

rum is licensed under the MIT License. See [`LICENSE`](./LICENSE) for the full text.

rum is a fork of [Pycord](https://github.com/Pycord-Development/pycord), which is
in turn a fork of [discord.py](https://github.com/Rapptz/discord.py). Code
inherited from those projects keeps its original copyright notice, and every
source file in this repository carries the notices of the authors it is derived
from.

Contributions are accepted under the same terms, see
[`CONTRIBUTING.md`](./CONTRIBUTING.md).

