"""Rewrite `../../<path>` markdown links to absolute GitHub URLs.

Used by the `mkdocs_philosophy_copy` Makefile target so that links pointing
outside the mkdocs `docs_dir` resolve to the file on GitHub instead of
producing "target not found among documentation files" warnings.

Usage:
    python3 tools/rewrite_doc_links.py <path> [<path> ...]

Each <path> may be a `.md` file or a directory (walked recursively). Files
are modified in place. The operation is idempotent.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

GITHUB_BASE = "https://github.com/vispy/GSP_API/blob/main"
LINK_RE = re.compile(r"\]\(\.\./\.\./([^)]+)\)")


def rewrite_file(path: Path) -> int:
    original = path.read_text(encoding="utf-8")
    rewritten, count = LINK_RE.subn(
        lambda m: f"]({GITHUB_BASE}/{m.group(1)})",
        original,
    )
    if count > 0:
        path.write_text(rewritten, encoding="utf-8")
    return count


def iter_markdown_files(target: Path):
    if target.is_dir():
        yield from sorted(target.rglob("*.md"))
    elif target.suffix == ".md" and target.is_file():
        yield target


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    total_files = 0
    total_links = 0
    for raw in argv[1:]:
        target = Path(raw)
        if not target.exists():
            print(f"warning: {target} does not exist, skipping", file=sys.stderr)
            continue
        for md in iter_markdown_files(target):
            count = rewrite_file(md)
            if count > 0:
                total_files += 1
                total_links += count
                print(f"  rewrote {count:3d} link(s) in {md}")

    print(f"rewrite_doc_links: {total_links} link(s) across {total_files} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
