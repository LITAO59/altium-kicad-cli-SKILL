#!/usr/bin/env python3
"""Print the CHANGELOG.md section for a given version to stdout.

Usage:
    python tools/changelog_extract.py <version>

Looks for a ``## [<version>]`` heading; falls back to ``## [Unreleased]``; then to a
one-line default. Used by the release workflow to build the GitHub Release notes.
Stdlib-only, no dependencies.
"""

from __future__ import annotations

import pathlib
import re
import sys

# Markdown link-reference definitions, e.g. ``[Unreleased]: https://...`` — kept out
# of the rendered release notes.
_LINK_DEF = re.compile(r"^\[[^\]]+\]:\s+\S")


def extract(text: str, version: str) -> str:
    """Return the changelog body for *version* (or the Unreleased section)."""
    lines = text.splitlines()

    def section(prefixes: list[str]) -> str | None:
        for i, line in enumerate(lines):
            low = line.strip().lower()
            if any(low.startswith(p) for p in prefixes):
                out: list[str] = []
                for nxt in lines[i + 1:]:
                    if nxt.startswith("## "):
                        break
                    if _LINK_DEF.match(nxt):
                        continue
                    out.append(nxt)
                body = "\n".join(out).strip()
                if body:
                    return body
        return None

    return (
        section([f"## [{version.lower()}]"])
        or section(["## [unreleased]"])
        or f"Release {version}."
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: changelog_extract.py <version>", file=sys.stderr)
        return 2
    changelog = pathlib.Path(__file__).resolve().parent.parent / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8") if changelog.exists() else ""
    print(extract(text, argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
