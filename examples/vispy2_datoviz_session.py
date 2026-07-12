"""Bounded experimental Datoviz session preview."""

from __future__ import annotations

import argparse

import gsp_vispy2 as vp


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--poll",
        action="store_true",
        help="own a non-blocking display and explicitly poll two frames",
    )
    args = parser.parse_args()

    figure, axes = vp.subplots()
    axes.scatter(
        [-0.7, -0.25, 0.2, 0.65],
        [-0.35, 0.4, -0.15, 0.3],
        size=[18.0, 28.0, 40.0, 54.0],
    )
    axes.set_xlim(-1.0, 1.0)
    axes.set_ylim(-1.0, 1.0)

    with vp.open_session("datoviz") as session:
        plan = session.inspect(figure, operation="display")
        plan.require_executable()
        if args.poll:
            display = session.show(figure, block=False)
            session.poll(display)
            session.poll(display)
        else:
            session.show(figure, block=True, frame_count=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
