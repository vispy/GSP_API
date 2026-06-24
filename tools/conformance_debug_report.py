#!/usr/bin/env python
"""Print the non-authoritative GSP conformance debug-json report."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "src"):
    path_text = str(path)
    if path_text not in sys.path:
        sys.path.insert(0, path_text)

from fixtures.conformance import conformance_debug_report_json


def main() -> int:
    sys.stdout.write(conformance_debug_report_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
