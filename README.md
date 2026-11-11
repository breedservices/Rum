<!-- readme-metadata
description: rum - a Discord API wrapper for Python, forked from Pycord
keywords: discord, discord-bot, python, async, pycord, rum, bot, api-wrapper
homepage: https://github.com/breedservices/Rum
-->

# rum

This is the **rum** Discord library — a fork of [Pycord](https://github.com/Pycord-Development/pycord).

rum is an async Python API wrapper for the Discord API, based on Pycord. It keeps the familiar API style while evolving independently.

## Documentation

There is no dedicated rum documentation site right now. You can rely on:

- The [`examples/`](./examples) directory in this repository
- [Pycord's documentation](https://docs.pycord.dev) for general API usage (most concepts and APIs are the same)
- Or read the actual source code
- Get an LLM to generate documentation

## Installation

rum is not published on PyPI. Install it directly from the repository URL:

```sh
# pip
pip install git+https://github.com/breedservices/Rum.git

# or with extras
pip install "rum[speed] @ git+https://github.com/breedservices/Rum.git"
pip install "rum[voice] @ git+https://github.com/breedservices/Rum.git"
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
  cache that persists to JSON files on disk with `msgspec`

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

Extras are selected with `--extra`, e.g. `uv sync --extra speed --extra voice`.

If you prefer pip, the extras must be quoted — otherwise the shell expands
`[speed]` as a glob pattern and fails with `zsh: no matches found: [speed]`:

```sh
uv pip install -e ".[speed]"
uv pip install -e ".[voice]"
```

The project metadata (summary and keywords) is derived from this file's
`readme-metadata` block by `scripts/readme_metadata.py`, so the README stays the
single source of truth. A CI job verifies the built package matches it.

## License

rum is based on Pycord and retains the upstream MIT license notices for Pycord-derived code. See [`LICENSE`](./LICENSE) for details.
