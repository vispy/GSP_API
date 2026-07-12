from __future__ import annotations

import json

import numpy as np

from gsp.qa.visual.artifacts import ensure_run_dirs, write_scene_artifacts
from gsp.qa.visual.cases import list_cases
from gsp.qa.visual.vispy2_acceptance import S051_SUITE, figure_to_visual_qa_scene
from vispy2 import subplots


def test_adapter_preserves_in_memory_protocol_records() -> None:
    fig, ax = subplots()
    visual = ax.scatter([0.0], [1.0], color=(1, 2, 3, 255), id="record:point")
    scene = figure_to_visual_qa_scene(fig, case_id="vispy2/unit")
    assert scene.visuals[0] is visual
    assert scene.views[0] is fig.views()[0]
    assert scene.arrays["record_point_positions"] is visual.positions


def test_s051_matrix_is_public_producer_authored_and_bounded() -> None:
    cases = list_cases(suite=S051_SUITE)
    assert [case.case_id for case in cases] == [
        "vispy2/primitives", "vispy2/scalar_image_colorbar", "vispy2/text",
        "vispy2/mesh", "vispy2/texture2d_boundary"]
    assert {visual.id for case in cases for visual in case.build().visuals} >= {
        "s051:point", "s051:marker", "s051:segment", "s051:path", "s051:image",
        "s051:text", "s051:mesh", "s051:texture-mesh"}


def test_s051_frozen_scene_artifact_has_array_sidecar(tmp_path) -> None:
    scene = list_cases(suite=S051_SUITE)[0].build()
    ensure_run_dirs(tmp_path)
    scene_path, arrays_path = write_scene_artifacts(tmp_path, scene)
    payload = json.loads(scene_path.read_text(encoding="utf-8"))
    with np.load(arrays_path) as arrays:
        assert set(payload["arrays"]) == set(arrays.files)
    assert payload["schema_kind"] == "gsp.visual_qa.scene"
