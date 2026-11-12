"""
Compatibility package for :mod:`rum`.

``import discord`` is kept working for backwards compatibility with Pycord.
rum is the actual library; this package simply re-exports it and makes the
``discord.*`` submodule tree resolve to the very same module objects, so
``isinstance`` checks and class identities stay consistent across both names.

:copyright: (c) 2015-2021 Rapptz & (c) 2021-present Pycord Development
:copyright: (c) 2026-present The rum team
:license: MIT, see LICENSE for more details.
"""

from __future__ import annotations

import sys
from importlib import import_module
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Any, Sequence

import rum as _rum

__all__ = getattr(_rum, "__all__", None) or [
    name for name in dir(_rum) if not name.startswith("_")
]

# Re-export the public API of rum so `discord.Client` etc. work.
for _name in dir(_rum):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_rum, _name)

# Keep the metadata in sync with rum.
__title__ = _rum.__title__
__author__ = _rum.__author__
__license__ = _rum.__license__
__copyright__ = _rum.__copyright__
__version__ = _rum.__version__
version_info = _rum.version_info


class _AliasFinder(MetaPathFinder):
    """Resolve ``discord.<sub>`` imports to the already-loaded ``rum.<sub>``."""

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None = None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        if not fullname.startswith("discord."):
            return None

        rum_name = "rum." + fullname[len("discord.") :]
        try:
            module = import_module(rum_name)
        except ImportError:
            return None

        spec = ModuleSpec(fullname, _AliasLoader(module))
        spec.submodule_search_locations = getattr(module, "__path__", None)
        return spec


class _AliasLoader:
    """Loader that returns an existing module instead of executing new code."""

    def __init__(self, module: ModuleType) -> None:
        self.module = module

    def create_module(self, spec: ModuleSpec) -> ModuleType:
        return self.module

    def exec_module(self, module: ModuleType) -> None:
        # The module already exists and is fully initialised.
        return None


# Make `import discord` return the rum module itself so that top level
# attributes (discord.Client, discord.Intents, ...) are the *same* objects.
sys.modules[__name__] = _rum
sys.meta_path.insert(0, _AliasFinder())
