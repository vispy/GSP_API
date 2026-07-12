"""Create the first GSP 0.2 scene shown in the public documentation."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import gsp_vispy2 as vp


def build_scene() -> vp.Figure:
    """Return a semantic producer figure using only the GSP 0.2 public API."""
    fig, ax = vp.subplots()
    x = np.array([0.0, 1.0, 2.0, 3.0], dtype=np.float32)
    y = np.array([0.4, 1.2, 0.7, 1.6], dtype=np.float32)
    values = np.array([0.2, 0.8, 0.5, 1.0], dtype=np.float32)

    points = ax.scatter(
        x,
        y,
        c=values,
        cmap="viridis",
        clim=(0.0, 1.0),
        size=72,
        id="visual:measurements",
    )
    ax.plot(x, y, color=(60, 70, 90, 255), width=1.5, id="visual:trend")
    ax.set_xlim(-0.25, 3.25)
    ax.set_ylim(0.0, 1.9)
    ax.set_xlabel("sample")
    ax.set_ylabel("response")
    ax.set_title("GSP 0.2 first scene")
    ax.grid(True)
    ax.colorbar(
        points.color_encoding.color_scale_id,
        label="quality",
        linked_visual_ids=(points.id,),
    )
    return fig


def main() -> None:
    """Save the scene through the portable Matplotlib reference path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("gsp-first-scene.png"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    build_scene().savefig(args.output, dpi=150)
    print(args.output)


if __name__ == "__main__":
    main()
