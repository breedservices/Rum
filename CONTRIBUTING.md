# Contributing to rum

Thanks for taking the time to contribute.

rum is a fork of [Pycord](https://github.com/Pycord-Development/pycord), maintained by the rum
team. Report issues against this repository, not upstream, unless the bug is inherited from
Pycord.

## Before you start

- **Questions:** use [Discussions](https://github.com/breedservices/Rum/discussions) when
  possible.
- **Bugs:** search existing issues first. Include a short summary, reproduction steps (small code
  sample, never include a token), expected vs actual behavior (full traceback if any), and your
  environment (rum version, Python version, OS, install method).
- **Scope:** keep changes focused. Read a few nearby files and match their naming, imports,
  structure, and error handling.

## Development setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and builds. Python
3.11+ is required.

```bash
# Create the environment and install dev/test dependencies
uv sync --group dev --group test --extra voice

# Run tests
uv run pytest

# Build sdist and wheel
uv build
```

Notes:

- Extras are selected with `--extra` (e.g. `uv sync --extra voice`, `uv sync --extra music`).
- In `zsh`, quote extras with pip/uv pip to avoid glob expansion: `uv pip install -e ".[voice]"`.
- `pre-commit` hooks are configured in `.pre-commit-config.yaml`. Install with
  `uv run pre-commit install` to run formatting/import sorting/pyupgrade on commit.

## Repository layout

```text
rum/                 library core: client, gateway, HTTP, cache, models, state, voice, UI, ...
  commands/          application command helpers
  ext/               extensions
    commands/        prefixed command framework
    tasks/           background task helpers
    pages/           pagination
    bridge/          bridge between slash and prefixed commands
    music/           Lavalink v4 / NodeLink v3 music client
  sinks/             audio sinks
  types/             typed payload definitions
  ui/                components, views, modals
  voice/             voice connections and receive
  webhook/           webhook clients
  bin/               bundled native binaries (e.g. libopus)
discord/             compatibility package resolving to the same modules as `rum`
docs/                MDX guides rendered on GitHub, plus generated `docs/api/`
examples/            runnable example bots
scripts/             maintenance and release scripts
tests/               pytest suite (including `tests/voice/`)
```

- `import rum` is canonical. `import discord` is a compatibility shim to the same modules.
- rum is its own library. Third-party addons (e.g. music/Lavalink helpers) may not know rum yet;
  prefer the public `rum` API and avoid private internals. Compatibility-oriented changes that help
  ecosystem tooling adopt rum are welcome when behavior remains correct.

## Documentation

- **Guides:** `docs/*.mdx` and `docs/ext/**` render directly on GitHub (no site build). Start at
  [`docs/index.mdx`](docs/index.mdx).
- **API reference:** `docs/api/` is generated from docstrings. After changing docstrings or public
  API, regenerate:

  ```bash
  uv run --with pypandoc-binary python docs/generate_reference.py
  ```

  Without pandoc, the generator falls back to emitting docstrings with Sphinx roles stripped.

## Code and tests

- Keep diffs focused; do not rename/reformat/tidy unrelated code.
- Prefer plain solutions and reuse existing helpers before adding abstractions.
- Follow existing cog/command/event layout when adding features.
- Add or update tests when behavior changes (`tests/`, run with `uv run pytest`).
- When suppressing a type checker warning, add a short reason (and error code for `type: ignore`).

Project metadata (`description`, `keywords`) comes from the `readme-metadata` block at the top of
`README.md` via `scripts/readme_metadata.py`; update that block rather than duplicating values.

## Changelog, commits, and pull requests

- **Changelog:** update `CHANGELOG.md` under `[Unreleased]` for user-facing or notable changes,
  following [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
- **Commits:** prefer [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
  subjects (e.g. `fix(cache): evict expired entries`, `docs: update quickstart`). Keep each commit
  to a single logical change.
- **Pull requests:** open against `master`. Describe the problem and fix, link relevant issues, and
  note anything not verified. CI must pass on the latest commit.

## Licensing

By submitting a pull request, you assert that you have the right to contribute the code and license
your contribution under the project's [MIT License](LICENSE). If you include code from another
project, keep its copyright and license notice in the files you add it to.

rum inherits code from [Pycord](https://github.com/Pycord-Development/pycord) and
[discord.py](https://github.com/Rapptz/discord.py); source files carry the notices of the authors
they are derived from.
