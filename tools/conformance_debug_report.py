#!/usr/bin/env python
"""Print the non-authoritative GSP conformance debug-json report."""

from __future__ import annotations

import sys

from fixtures.conformance import conformance_debug_report_json


def main() -> int:
    sys.stdout.write(conformance_debug_report_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
