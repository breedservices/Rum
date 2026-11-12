# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) when
possible (see our [Version Guarantees](docs/version_guarantees.mdx) for more info).

## [Unreleased]

These changes are available on the `master` branch, but have not yet been released.

### Added

### Changed

### Fixed

### Deprecated

### Removed

## [0.2.0] - 2026-11-12

### Added

- Added per-kind cache rules (`CacheKind`, `CacheRule`, `RuledCache`,
  `DefaultCacheProvider.cache_for` / `rule_for`) so caches can be enabled, capped,
  given a TTL, or trimmed to selected fields per kind.
- Added `examples/cache_rules.py` demonstrating cache rules.
- Added support for `session_start_limit.max_concurrency`: `AutoShardedClient`
  identifies shards in batches of the allowed size, waiting five seconds between
  batches, and `HTTPClient.get_bot_gateway` now returns the concurrency limit.
- Added a generated API reference under `docs/api/` (one page per module) and
  `docs/generate_reference.py` to regenerate it from docstrings.
- Added a sharding section to the quickstart guide.
- Added `rum.ext.music`, a Lavalink v4 and NodeLink v3 client (node pool,
  `VoiceProtocol` player, track loading, queue, filters, events, and REST helpers).
  Select the server with `server_type="lavalink"` or `server_type="nodelink"` when
  creating a node. It uses rum's built-in HTTP/WebSocket transport (no `aiohttp`
  dependency), does not depend on the `voice` extra, and supports custom queue
  providers (e.g. disk/database-backed) instead of the default in-memory queue.

### Changed

- Replaced the Sphinx documentation with MDX pages that render directly on GitHub
  (`docs/*.mdx`, `docs/ext/**`); the guides and extension docs are now plain
  Markdown/MDX with links to the generated API reference and `CHANGELOG.md`.
- Switched the packaging backend from setuptools to Hatchling, with dependencies and
  extras declared in `pyproject.toml`.
- Made `msgspec` a required dependency (used for JSON encoding/decoding across the
  library) and removed the `[speed]` extra.
- Replaced the `zstandard` dependency (Python < 3.14) with `backports.zstd` and
  unified gateway zstd decompression on the stdlib-compatible API.
- Cleaned up the examples: fixed lint issues, renamed the duplicate
  `pagetest_target` prefix command to `pagetest_target_prefix`, and made the
  background/async examples read the bot token from `BOT_TOKEN`.

### Removed

- Removed the Sphinx build and its infrastructure (`docs/conf.py`,
  `docs/extensions/`, templates/static assets, `docs/build/`, `docs/locales/`,
  `docs/Makefile`, `make.bat`, and the `.rst` sources).
- Removed Read the Docs and Crowdin configuration and workflows
  (`.readthedocs.yml`, `crowdin.yml`, docs-check/localization/export workflows, and
  the related release scripts).
- Removed the `docs` optional-dependency/requirements set and the setuptools
  packaging files (`setup.py`, `MANIFEST.in`, `requirements/*.txt`) replaced by the
  Hatchling configuration.

[unreleased]: https://github.com/breedservices/Rum/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/breedservices/Rum/releases/tag/v0.2.0
