"""API review example: S044 View3D mesh triangle picking.

The rendered scene shows a shallow triangular prism with a raised magenta pick face. The scripted
report uses the Matplotlib CPU oracle to demonstrate the public S044 pick payload: hit identity,
miss, and stale snapshot handling. Datoviz live interaction may orbit/pan/zoom the rendered View3D
scene, but Datoviz intentionally keeps the S044 mesh-pick query capability unadvertised.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json

import numpy as np

from _review_runner import ReviewScene, run_review
from gsp.protocol import (
    Camera3D,
    CoordinateSpace,
    MeshColorMode,
    MeshVisual,
    OrthographicProjection3D,
    PanelTextGuide,
    PanelTextRole,
    View3D,
    View3DMeshTrianglePickRequest,
    project_view3d_data_point,
    resolve_view3d_projection_snapshot,
)
from gsp_matplotlib.protocol_query import (
    QueryVisualEntry,
    query_view3d_mesh_triangle_pick,
)

PANEL_BOUNDS = (0.0, 1280.0, 0.0, 720.0)
LAYOUT_SNAPSHOT_ID = "layout:mesh-pick-review"


def _pick_mesh() -> MeshVisual:
    positions = np.array(
        [
            [-0.82, -0.62, 0.00],
            [0.82, -0.62, 0.00],
            [0.00, 0.72, 0.00],
            [-0.58, -0.40, 0.62],
            [0.92, -0.40, 0.62],
            [0.17, 0.86, 0.62],
        ],
        dtype=np.float32,
    )
    faces = np.array(
        [
            [0, 1, 2],
            [3, 4, 5],
            [0, 1, 4],
            [0, 4, 3],
            [1, 2, 5],
            [1, 5, 4],
            [2, 0, 3],
            [2, 3, 5],
        ],
        dtype=np.uint32,
    )
    colors = np.array(
        [
            [30, 136, 229, 255],
            [216, 27, 96, 255],
            [244, 162, 97, 255],
            [244, 162, 97, 255],
            [42, 157, 143, 255],
            [42, 157, 143, 255],
            [87, 117, 144, 255],
            [87, 117, 144, 255],
        ],
        dtype=np.uint8,
    )
    return MeshVisual(
        id="visual:pick-overlap",
        positions=positions,
        faces=faces,
        coordinate_space=CoordinateSpace.DATA,
        color=colors,
        color_mode=MeshColorMode.FACE,
    )


def _view3d() -> View3D:
    return View3D(
        id="view:mesh-pick",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(2.2, -3.1, 2.4),
            target=(0.08, 0.0, 0.28),
            up=(0.0, 0.0, 1.0),
        ),
        projection=OrthographicProjection3D(
            xlim=(-1.65, 1.65),
            ylim=(-1.18, 1.18),
            near_far=(0.0, 8.0),
        ),
    )


def _panel_xy_from_data(view: View3D, point: tuple[float, float, float]) -> tuple[float, float]:
    ndc = project_view3d_data_point(view, point)
    left, right, bottom, top = PANEL_BOUNDS
    return (
        left + (ndc[0] + 1.0) * 0.5 * (right - left),
        bottom + (ndc[1] + 1.0) * 0.5 * (top - bottom),
    )


def _pick_report() -> list[dict[str, object]]:
    view = _view3d()
    mesh = _pick_mesh()
    snapshot = resolve_view3d_projection_snapshot(
        view, layout_snapshot_id=LAYOUT_SNAPSHOT_ID
    )
    hit_xy = _panel_xy_from_data(view, (0.14, -0.02, 0.62))
    requests = (
        (
            "frontmost-hit",
            View3DMeshTrianglePickRequest(
                view_id=view.id,
                panel_id=view.panel_id,
                panel_xy=hit_xy,
                expected_layout_snapshot_id=snapshot.layout_snapshot_id,
                expected_view_revision=snapshot.view_revision,
                expected_view_projection_snapshot_id=snapshot.view_projection_snapshot_id,
            ),
        ),
        (
            "miss",
            View3DMeshTrianglePickRequest(
                view_id=view.id,
                panel_id=view.panel_id,
                panel_xy=(120.0, 92.0),
                expected_layout_snapshot_id=snapshot.layout_snapshot_id,
                expected_view_revision=snapshot.view_revision,
                expected_view_projection_snapshot_id=snapshot.view_projection_snapshot_id,
            ),
        ),
        (
            "stale-pick-scene",
            View3DMeshTrianglePickRequest(
                view_id=view.id,
                panel_id=view.panel_id,
                panel_xy=hit_xy,
                expected_layout_snapshot_id=snapshot.layout_snapshot_id,
                expected_view_revision=snapshot.view_revision,
                expected_view_projection_snapshot_id=snapshot.view_projection_snapshot_id,
                expected_pick_scene_snapshot_id="pick-scene:stale",
            ),
        ),
    )
    rows: list[dict[str, object]] = []
    for label, request in requests:
        result = query_view3d_mesh_triangle_pick(
            request,
            [QueryVisualEntry(mesh)],
            view=view,
            snapshot=snapshot,
            panel_bounds=PANEL_BOUNDS,
        )
        payload = result.extension_payload
        payload_data = asdict(payload) if is_dataclass(payload) else {}
        rows.append(
            {
                "label": label,
                "status": result.status.value,
                "hit": result.hit,
                "visual_id": result.visual_id,
                "primitive_index": result.item_id,
                "panel_xy": tuple(round(value, 2) for value in request.panel_xy),
                "diagnostic": result.diagnostic,
                "payload": payload_data,
            }
        )
    return rows


def build_scene() -> ReviewScene:
    return ReviewScene(
        title="S044 mesh triangle pick",
        view3d=_view3d(),
        visuals=(_pick_mesh(),),
        panel_text_guides=(
            PanelTextGuide(
                id="guide:title",
                panel_id="panel:main",
                role=PanelTextRole.TITLE,
                text="S044 mesh triangle pick",
            ),
        ),
        notes=(
            "The raised magenta top face should win the scripted frontmost pick.",
            "The side faces make Datoviz and Matplotlib live View3D orbit visibly change the shape.",
            "The report printed by this script is generated by the Matplotlib CPU oracle.",
            "Datoviz must keep query.view3d.mesh_triangle_pick.v1 unadvertised until native public identity and freshness are proven.",
        ),
    )


if __name__ == "__main__":
    print(json.dumps({"s044_pick_report": _pick_report()}, indent=2, default=str))
    raise SystemExit(run_review(build_scene))
