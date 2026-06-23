"""CLI for the S023 visual QA harness."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from gsp.qa.visual.cases import S023_SUITE, list_cases
from gsp.qa.visual.runner import run_visual_qa_suite


def main(argv: Sequence[str] | None = None) -> int:
    """Run the visual QA CLI."""
    parser = argparse.ArgumentParser(prog="python -m gsp.qa.visual")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list visual QA cases")
    list_parser.add_argument("--suite", default=S023_SUITE)

    run_parser = subparsers.add_parser("run", help="run visual QA cases")
    run_parser.add_argument("--suite", default=S023_SUITE)
    run_parser.add_argument("--backends", default="matplotlib,datoviz")
    run_parser.add_argument("--out", required=True)
    run_parser.add_argument("--case", action="append", dest="cases", default=[])
    run_parser.add_argument("--contact-sheet", action="store_true")
    run_parser.add_argument("--no-contact-sheet", action="store_true")
    run_parser.add_argument("--resolution", default="800x600")
    run_parser.add_argument("--run-id", default=None)

    args = parser.parse_args(argv)
    if args.command == "list":
        for case in list_cases(suite=args.suite):
            print(f"{case.case_id}\t{case.family}\t{case.title}")
        return 0
    if args.command == "run":
        width, height = _parse_resolution(args.resolution)
        contact_sheet = bool(args.contact_sheet or not args.no_contact_sheet)
        report = run_visual_qa_suite(
            suite=args.suite,
            out_dir=Path(args.out),
            backends=tuple(part.strip() for part in args.backends.split(",") if part.strip()),
            case_ids=tuple(args.cases),
            contact_sheet=contact_sheet,
            run_id=args.run_id,
            resolution=(width, height),
        )
        print(report["report_path"] if "report_path" in report else str(Path(args.out) / "report.json"))
        return 0
    raise AssertionError(f"unhandled command: {args.command}")


def _parse_resolution(value: str) -> tuple[int, int]:
    try:
        width_text, height_text = value.lower().split("x", maxsplit=1)
        width = int(width_text)
        height = int(height_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("resolution must look like WIDTHxHEIGHT") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("resolution dimensions must be positive")
    return width, height
