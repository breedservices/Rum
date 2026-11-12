# Contributing to rum

Thanks for taking the time to contribute.

rum is a fork of [Pycord](https://github.com/Pycord-Development/pycord), maintained by The rum
team. Report issues against this repository, not upstream, unless the bug is inherited from
Pycord.

These guidelines describe how the project is developed. Where a rule is enforced (by the test
suite, CI, or the configured linters/formatters), keep changes consistent with it. If a rule is
not enforced yet, enforcing it is a welcome contribution.

## Questions and bug reports

- Use [discussions](https://github.com/breedservices/Rum/discussions) for questions when possible.
- Search existing issues before opening a new one.
- Bug reports need enough information to be actionable: a short summary, steps to reproduce (a
  small code sample is best — never include a token), what you expected, what actually happened
  (full traceback if there is one), and your environment (rum version, Python version, OS, how it
  was installed).

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and builds. Python
3.11+ is required.

```bash
# Create the environment and install the dev/test dependencies
uv sync --group dev --group test --extra voice

# Run the tests
uv run pytest

# Build the sdist and wheel
uv build
```

Extras are selected with `--extra`, e.g. `uv sync --extra speed --extra voice`. With pip, quote
extras so the shell does not expand them as globs:

```sh
uv pip install -e ".[speed]"
uv pip install -e ".[voice]"
```

`pre-commit` hooks are configured in `.pre-commit-config.yaml` (formatting, import sorting,
pyupgrade, etc.). Install them with `uv run pre-commit install` if you want them to run on commit.

## Layout

```
rum/                 the library: client, gateway, HTTP, cache, models, state, voice, UI, ...
  commands/          application command helpers
  ext/               extensions
    commands/        prefixed command framework
    tasks/           background task helpers
    pages/           pagination
    bridge/          bridge between slash and prefixed commands
  sinks/             audio sinks
  types/             typed payload definitions
  ui/                components, views, modals
  voice/             voice connections and receive
  webhook/           webhook clients
  bin/               bundled native binaries (e.g. libopus)
discord/             compatibility package that resolves to the same modules as `rum`
docs/                guides and extension docs as MDX (rendered on GitHub), plus `docs/api/`
examples/            runnable example bots
scripts/             maintenance and release scripts
tests/               pytest suite (including `tests/voice/`)
```

`import rum` is the canonical import. `import discord` is a compatibility shim that resolves to the
same modules.

rum is its own library. Third-party addons (music/Lavalink clients, helpers, etc.) may not know
about rum yet; when integrating or writing one, prefer the public `rum` API and avoid relying on
private internals. Compatibility-oriented changes that make the API easier for existing
discord.py/Pycord ecosystem tooling to adopt are welcome, but keep behaviour correct for rum.

## Documentation

- Guides live in `docs/` as MDX and render directly on GitHub (no site build). Start at
  [`docs/index.mdx`](docs/index.mdx).
- The API reference under `docs/api/` is generated from docstrings. After changing a docstring,
  regenerate it:

  ```bash
  uv run --with pypandoc-binary python docs/generate_reference.py
  ```

  (Without pandoc the generator falls back to emitting the docstrings with Sphinx roles stripped.)

## Code and tests

- Read a few nearby files first and match their naming, imports, structure, and error handling.
- Keep diffs focused on the task. Do not rename, reformat, or tidy unrelated code.
- Prefer the plain solution; reuse existing helpers before adding new ones. Avoid speculative
  abstractions.
- Follow the existing cog/command/event layout when adding features.
- Add or update tests when behaviour changes. Tests live under `tests/` and run with `pytest`.
  The full suite is `uv run pytest` (`78 passed, 2 skipped` at the time of writing).
- When a type checker warning must be suppressed, leave a short comment explaining why (and include
  the error code for `type: ignore`).

Project metadata (`description`, `keywords`) is derived from the `readme-metadata` block at the top
of `README.md` by `scripts/readme_metadata.py`; update that block rather than duplicating the
values elsewhere.

## Changelog, commits, and pull requests

- Update `CHANGELOG.md` under `[Unreleased]` for user-facing or notable changes, following
  [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
- Prefer [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) style subjects
  (e.g. `fix(cache): evict expired entries`, `docs: update quickstart`). Keep commits focused on a
  single logical change.
- Open pull requests against `master`. Describe the problem and the fix, link any relevant issue,
  and note anything you did not verify. CI must pass on the latest commit.

## Licensing

By submitting a pull request, you assert that you have the right to contribute the code and you
license your contribution under the project's [MIT License](LICENSE), the same terms as the rest of
the repository. If you include code from another project, keep its copyright and license notice in
the files you add it to.

rum inherits code from [Pycord](https://github.com/Pycord-Development/pycord) and
[discord.py](https://github.com/Rapptz/discord.py); source files carry the notices of the authors
they are derived from.
