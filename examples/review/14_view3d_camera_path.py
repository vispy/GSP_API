"""API review example: deterministic View3D camera path.

The script applies a small sequence of canonical S037 View3D navigation actions, prints the
accepted revisions/snapshot ids, and renders the final camera state. It demonstrates producer-side
camera-path logic without adding animation, perspective, or backend-native controller semantics.
"""

from __future__ import annotations

import json
from math import pi

import numpy as np

from _review_runner import ReviewScene, run_review
from gsp.protocol import (
    Camera3D,
    CoordinateSpace,
    MeshColorMode,
    MeshVisual,
    Orbit3DPayload,
    OrthographicProjection3D,
    Pan3DPayload,
    PanelTextGuide,
    PanelTextRole,
    View3D,
    View3DNavigationAction,
    View3DNavigationActionKind,
    Zoom3DPayload,
    apply_view3d_navigation_action,
    resolve_view3d_projection_snapshot,
)

LAYOUT_SNAPSHOT_ID = "layout:camera-path-review"


def _home_view3d() -> View3D:
    return View3D(
        id="view:camera-path",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(3.2, -3.6, 2.7),
            target=(0.0, 0.0, 0.1),
            up=(0.0, 0.0, 1.0),
        ),
        projection=OrthographicProjection3D(
            xlim=(-2.8, 2.8),
            ylim=(-2.0, 2.0),
            near_far=(0.0, 9.0),
        ),
    )


def _apply_action(
    view: View3D,
    kind: View3DNavigationActionKind,
    payload: Orbit3DPayload | Pan3DPayload | Zoom3DPayload,
) -> tuple[View3D, dict[str, object]]:
    snapshot = resolve_view3d_projection_snapshot(
        view, layout_snapshot_id=LAYOUT_SNAPSHOT_ID
    )
    action = View3DNavigationAction(
        kind=kind,
        view_id=view.id,
        base_view_revision=view.revision,
        base_view_projection_snapshot_id=snapshot.view_projection_snapshot_id,
        base_layout_snapshot_id=snapshot.layout_snapshot_id,
        payload=payload,
    )
    result = apply_view3d_navigation_action(
        view, action, layout_snapshot_id=LAYOUT_SNAPSHOT_ID
    )
    if not result.accepted or result.view is None:
        raise RuntimeError(f"navigation rejected: {result.diagnostics}")
    row = {
        "action": kind.value,
        "old_revision": result.old_revision,
        "new_revision": result.new_revision,
        "snapshot": result.view_projection_snapshot_id,
        "eye": tuple(round(value, 4) for value in result.view.camera.eye),
        "target": tuple(round(value, 4) for value in result.view.camera.target),
        "xlim": tuple(round(value, 4) for value in result.view.projection.xlim),
        "ylim": tuple(round(value, 4) for value in result.view.projection.ylim),
    }
    return result.view, row


def _camera_path() -> tuple[View3D, list[dict[str, object]]]:
    view = _home_view3d()
    rows: list[dict[str, object]] = []
    for kind, payload in (
        (
            View3DNavigationActionKind.ORBIT,
            Orbit3DPayload(delta_yaw_radians=-0.32 * pi, delta_pitch_radians=0.12 * pi),
        ),
        (
            View3DNavigationActionKind.PAN,
            Pan3DPayload(delta_view_right=0.28, delta_view_up=-0.18),
        ),
        (
            View3DNavigationActionKind.ZOOM,
            Zoom3DPayload(scale=0.78),
        ),
    ):
        view, row = _apply_action(view, kind, payload)
        rows.append(row)
    return view, rows


def _mesh() -> MeshVisual:
    positions = np.array(
        [
            [-1.4, -0.9, -0.18],
            [1.4, -0.9, -0.18],
            [1.4, 0.9, -0.18],
            [-1.4, 0.9, -0.18],
            [-0.9, -0.48, 0.58],
            [0.9, -0.48, 0.58],
            [0.72, 0.52, 0.58],
            [-0.72, 0.52, 0.58],
            [0.0, 0.0, 1.25],
        ],
        dtype=np.float32,
    )
    faces = np.array(
        [
            [0, 1, 2],
            [0, 2, 3],
            [4, 5, 8],
            [5, 6, 8],
            [6, 7, 8],
            [7, 4, 8],
            [0, 1, 5],
            [0, 5, 4],
            [1, 2, 6],
            [1, 6, 5],
            [2, 3, 7],
            [2, 7, 6],
            [3, 0, 4],
            [3, 4, 7],
        ],
        dtype=np.uint32,
    )
    colors = np.array(
        [
            [69, 123, 157, 255],
            [69, 123, 157, 255],
            [230, 57, 70, 255],
            [244, 162, 97, 255],
            [42, 157, 143, 255],
            [38, 70, 83, 255],
            [118, 200, 147, 255],
            [118, 200, 147, 255],
            [129, 178, 154, 255],
            [129, 178, 154, 255],
            [233, 196, 106, 255],
            [233, 196, 106, 255],
            [87, 117, 144, 255],
            [87, 117, 144, 255],
        ],
        dtype=np.uint8,
    )
    return MeshVisual(
        id="visual:camera-path-mesh",
        positions=positions,
        faces=faces,
        coordinate_space=CoordinateSpace.DATA,
        color=colors,
        color_mode=MeshColorMode.FACE,
    )


def build_scene() -> ReviewScene:
    final_view, _ = _camera_path()
    return ReviewScene(
        title="View3D camera path",
        view3d=final_view,
        visuals=(_mesh(),),
        panel_text_guides=(
            PanelTextGuide(
                id="guide:title",
                panel_id="panel:main",
                role=PanelTextRole.TITLE,
                text="View3D camera path",
            ),
        ),
        notes=(
            "Applies canonical orbit, pan, and zoom actions before rendering the final View3D state.",
            "The printed report records accepted revisions and projection snapshot ids.",
        ),
    )


if __name__ == "__main__":
    _, report = _camera_path()
    print(json.dumps({"view3d_camera_path": report}, indent=2))
    raise SystemExit(run_review(build_scene))
