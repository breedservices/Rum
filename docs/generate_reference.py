"""
Generates the API reference under ``docs/api`` as MDX from the docstrings.

The docs are read on GitHub, so every page is plain Markdown/GFM wrapped in
MDX: no Sphinx and no site build. Docstrings are written in reStructuredText,
so they are converted with pandoc when it is available::

    uv run --with pypandoc-binary python docs/generate_reference.py

Without pypandoc the docstrings are emitted as-is, with the Sphinx roles
stripped, which is enough to be readable but keeps the reST markup.
"""

from __future__ import annotations

import importlib
import inspect
import os
import pkgutil
import re
import shutil
from pathlib import Path
from typing import Any

import rum
import rum.ext

try:
    import pypandoc
except ImportError:  # pragma: no cover - the fallback is only for convenience
    pypandoc = None

DOCS = Path(__file__).parent / "api"

ROLE_RE = re.compile(
    r":(?:class|meth|attr|func|exc|data|obj|mod|const|term):`~?([^`<]+?)(?:\s*<[^`>]+>)?`"
)
SUBST_RE = re.compile(r"\|(coro|maybecoro|coroutine_link)\|_?")
ADMONITION_RE = re.compile(
    r'<div class="(attention|note|warning|tip|caution|danger)">\s*\n(.*?)\n\s*</div>',
    re.DOTALL,
)
VERSION_RE = re.compile(
    r'<div class="version(added|changed|deprecated)">\s*\n\s*(.*?)\s*\n\s*</div>',
    re.DOTALL,
)
OBJECT_RE = re.compile(r"<object object at 0x[0-9a-f]+>")

_rendered: dict[str, str] = {}


def render(text: str) -> str:
    if not text:
        return ""
    if text in _rendered:
        return _rendered[text]

    text = re.sub(r"^:(copyright|license):.*$", "", text, flags=re.MULTILINE)
    text = ROLE_RE.sub(lambda m: f"``{m.group(1)}``", text)
    text = SUBST_RE.sub(
        lambda m: (
            "*(coroutine)*"
            if m.group(1) == "coro"
            else "*(may be a coroutine)*"
            if m.group(1) == "maybecoro"
            else "coroutine"
        ),
        text,
    )

    if pypandoc is not None:
        text = pypandoc.convert_text(
            text,
            "gfm",
            format="rst",
            extra_args=["--wrap=none", "--shift-heading-level-by=3"],
        )

    text = VERSION_RE.sub(
        lambda m: f"*{m.group(1).capitalize()} in {m.group(2).rstrip('.')}.*", text
    )
    text = ADMONITION_RE.sub(
        lambda m: (
            f"> **{m.group(1).capitalize()}**\n>\n"
            + "\n".join(
                f"> {line}".rstrip(" ") for line in m.group(2).strip().splitlines()
            )
        ),
        text,
    )
    text = re.sub(r"\bpy:([a-zA-Z_]+)", r"\1", text)
    text = text.replace("\\|", "|")
    text = re.sub(r"^``` +$", "```", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    _rendered[text] = text
    return text


def signature(obj: Any) -> str:
    try:
        value = str(inspect.signature(obj))
    except (ValueError, TypeError):
        return "(...)"
    value = re.sub(r"([:>]) '([^']*)'", r"\1 \2", value)
    return OBJECT_RE.sub("...", value)


def method_signature(func: Any) -> str:
    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        return "(...)"
    params = list(sig.parameters.values())
    if params and params[0].name in ("self", "cls"):
        params = params[1:]
    value = str(sig.replace(parameters=params))
    value = re.sub(r"([:>]) '([^']*)'", r"\1 \2", value)
    return OBJECT_RE.sub("...", value)


def docstring(obj: Any) -> str:
    text = inspect.getdoc(obj) or ""
    if text.startswith("The MIT License (MIT)"):
        return ""
    return render(text)


def members(cls: type) -> list[tuple[str, Any]]:
    found = []
    for name, member in vars(cls).items():
        if name.startswith("_"):
            continue
        if isinstance(member, (staticmethod, classmethod)):
            member = member.__func__
        if inspect.isfunction(member):
            found.append((name, member))
    return found


def module_page(module: Any, paths: dict[str, str]) -> str:
    name = module.__name__
    is_package = hasattr(module, "__path__")
    lines = [f"# `{name}`", ""]

    module_doc = docstring(module)
    if module_doc:
        lines += [module_doc, ""]

    classes = [
        obj
        for obj in vars(module).values()
        if inspect.isclass(obj)
        and obj.__module__ == name
        and not obj.__name__.startswith("_")
    ]
    functions = [
        obj
        for obj in vars(module).values()
        if inspect.isfunction(obj)
        and obj.__module__ == name
        and not obj.__name__.startswith("_")
    ]

    if classes:
        lines.append("## Classes")
        lines.append("")
        for cls in sorted(classes, key=lambda c: c.__name__):
            lines.append(f"### `{cls.__name__}`")
            lines.append("")
            lines.append("```python")
            lines.append(f"class {cls.__name__}{signature(cls)}")
            lines.append("```")
            lines.append("")
            class_doc = docstring(cls)
            if class_doc:
                lines += [class_doc, ""]
            for method_name, method in members(cls):
                lines.append(f"#### `{method_name}()`")
                lines.append("")
                lines.append("```python")
                lines.append(f"{method_name}{method_signature(method)}")
                lines.append("```")
                lines.append("")
                method_doc = docstring(method)
                if method_doc:
                    lines += [method_doc, ""]

    if functions:
        lines.append("## Functions")
        lines.append("")
        for func in sorted(functions, key=lambda f: f.__name__):
            lines.append(f"### `{func.__name__}()`")
            lines.append("")
            lines.append("```python")
            lines.append(f"{func.__name__}{signature(func)}")
            lines.append("```")
            lines.append("")
            func_doc = docstring(func)
            if func_doc:
                lines += [func_doc, ""]

    if is_package:
        children = sorted(
            info.name
            for info in pkgutil.iter_modules(module.__path__)
            if not info.name.startswith("_")
        )
        if children:
            lines.append("## Modules")
            lines.append("")
            for child in children:
                full_name = f"{name}.{child}"
                if full_name in paths:
                    target = os.path.relpath(
                        paths[full_name], os.path.dirname(paths[name])
                    )
                    lines.append(f"- [`{full_name}`]({target}.mdx)")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    modules = []
    for package in (rum, rum.ext):
        modules.extend(
            info.name
            for info in pkgutil.walk_packages(package.__path__, package.__name__ + ".")
            if not any(part.startswith("_") for part in info.name.split("."))
        )
    for package in (rum, rum.ext):
        if package.__name__ not in modules:
            modules.append(package.__name__)

    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)

    paths = {}
    loaded = []
    for name in modules:
        module = importlib.import_module(name)
        relative = name.replace(".", "/")
        if hasattr(module, "__path__"):
            relative += "/index"
        paths[name] = relative
        loaded.append((name, module))

    for name, module in loaded:
        target = DOCS / f"{paths[name]}.mdx"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(module_page(module, paths), encoding="utf-8")

    index = ["# API Reference", "", "Generated from the docstrings in `rum`.", ""]
    for name in sorted(paths):
        index.append(f"- [`{name}`]({paths[name]}.mdx)")

    (DOCS / "index.mdx").write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"Wrote {len(paths)} module pages and the index to {DOCS}")


if __name__ == "__main__":
    main()
