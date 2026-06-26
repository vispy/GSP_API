"""Tests for the first Matplotlib/reference query proof."""

import numpy as np

import pytest

from gsp.protocol import (
    ColorMapId,
    ColorMapRef,
    ColorScale,
    CoordinateSpace,
    ImageOrigin,
    ImageVisual,
    LinearNormalize,
    MESH_QUERY_PAYLOAD_KIND,
    SCALAR_COLOR_QUERY_PAYLOAD_KIND,
    MeshColorMode,
    MeshQueryPayload,
    MeshVisual,
    MarkerShape,
    MarkerVisual,
    PointVisual,
    QueryContributionKind,
    QueryHit,
    QueryHitPolicy,
    QueryRequest,
    QueryResult,
    QueryScope,
    QueryStatus,
    ScalarColorEncoding,
    ScalarColorQueryPayload,
    ScalarColorSlot,
    ScalarRangeClass,
    TEXT_QUERY_PAYLOAD_KIND,
    TRANSFORM_QUERY_PAYLOAD_KIND,
    TextVisual,
    TransformQueryPayload,
    View2D,
    VisualFamily,
    VisualTransformBinding,
)
from gsp_matplotlib.color_mapping import map_scalar_value
from gsp_matplotlib.protocol_query import (
    QueryVisualEntry,
    failed_query_result,
    query_visuals,
    unsupported_query_result,
)


def test_query_returns_frontmost_point_over_image():
    """A point above an image wins with frontmost hit policy."""
    image = ImageVisual(
        id="visual:image",
        image=np.array(
            [
                [[10, 20, 30, 255], [40, 50, 60, 255]],
                [[70, 80, 90, 255], [100, 110, 120, 255]],
            ],
            dtype=np.uint8,
        ),
        extent=(-1.0, 1.0, -1.0, 1.0),
        origin=ImageOrigin.UPPER,
    )
    points = PointVisual(
        id="visual:points",
        positions=np.array([[0.25, 0.25]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([0.25], dtype=np.float32),
    )

    result = query_visuals(
        QueryRequest(id="query:point", panel_id="panel:main", coordinate=(0.25, 0.25)),
        [QueryVisualEntry(image, z_order=0), QueryVisualEntry(points, z_order=1)],
    )

    assert result.status == QueryStatus.HIT
    assert result.hits == (
        QueryHit(
            contribution_kind=QueryContributionKind.DATA,
            visual_id="visual:points",
            visual_family=VisualFamily.POINT,
            item_id=0,
            visual_coordinate=(0.25, 0.25),
            data_coordinate=(0.25, 0.25),
            displayed_rgba=(1.0, 0.0, 0.0, 1.0),
        ),
    )
    assert result.visual_family == VisualFamily.POINT
    assert result.visual_id == "visual:points"
    assert result.item_id == 0
    assert result.displayed_rgba == (1.0, 0.0, 0.0, 1.0)


def test_query_returns_image_texel_and_value():
    """Image query reports texel coordinates, displayed RGBA, and source value."""
    image = ImageVisual(
        id="visual:image",
        image=np.array(
            [
                [[10, 20, 30, 255], [40, 50, 60, 255]],
                [[70, 80, 90, 255], [100, 110, 120, 255]],
            ],
            dtype=np.uint8,
        ),
        extent=(-1.0, 1.0, -1.0, 1.0),
        origin=ImageOrigin.UPPER,
    )

    result = query_visuals(
        QueryRequest(id="query:image", panel_id="panel:main", coordinate=(0.75, 0.75)),
        [QueryVisualEntry(image)],
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_family == VisualFamily.IMAGE
    assert result.texel == (0, 1)
    assert result.value == (40, 50, 60, 255)
    assert result.displayed_rgba == (40 / 255.0, 50 / 255.0, 60 / 255.0, 1.0)


def test_query_scalar_image_returns_color_mapping_payload():
    """Scalar image query reports the canonical displayed RGBA and mapping details."""
    scale = _test_color_scale(colormap_id=ColorMapId.GRAY)
    image = ImageVisual(
        id="visual:image",
        image=np.array([[0.0, 0.5]], dtype=np.float32),
        extent=(0.0, 2.0, 0.0, 1.0),
        origin=ImageOrigin.LOWER,
        color_scale_id=scale.id,
    )

    result = query_visuals(
        QueryRequest(id="query:image", panel_id="panel:main", coordinate=(1.25, 0.5)),
        [QueryVisualEntry(image)],
        color_scales={scale.id: scale},
    )

    mapped = map_scalar_value(0.5, scale)
    assert result.status == QueryStatus.HIT
    assert result.texel == (0, 1)
    assert result.displayed_rgba == mapped.displayed_rgba
    assert result.extension_payload_kind == SCALAR_COLOR_QUERY_PAYLOAD_KIND
    assert result.extension_payload == ScalarColorQueryPayload(
        visual_id="visual:image",
        item_kind="texel",
        texel=(0, 1),
        color_slot=ScalarColorSlot.IMAGE,
        color_scale_id=scale.id,
        colormap_id="gray",
        source_value=0.5,
        normalized_value_raw=0.5,
        normalized_value_clipped=0.5,
        range_class=ScalarRangeClass.IN_RANGE,
        lut_index=128,
        displayed_rgba=mapped.displayed_rgba,
    )


def test_query_scalar_point_returns_color_mapping_payload():
    """Point scalar query includes item identity and range classification."""
    scale = _test_color_scale(colormap_id=ColorMapId.GRAY)
    points = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0], [4.0, 0.0]], dtype=np.float32),
        sizes=np.array([4.0, 4.0], dtype=np.float32),
        color_encoding=ScalarColorEncoding(
            slot=ScalarColorSlot.COLOR,
            values=np.array([-1.0, 2.0], dtype=np.float32),
            color_scale_id=scale.id,
        ),
    )

    result = query_visuals(
        QueryRequest(id="query:points", panel_id="panel:main", coordinate=(4.0, 0.0)),
        [QueryVisualEntry(points)],
        color_scales={scale.id: scale},
    )

    mapped = map_scalar_value(2.0, scale)
    assert result.status == QueryStatus.HIT
    assert result.visual_family == VisualFamily.POINT
    assert result.item_id == 1
    assert result.value == 2.0
    assert result.displayed_rgba == mapped.displayed_rgba
    assert result.extension_payload_kind == SCALAR_COLOR_QUERY_PAYLOAD_KIND
    assert result.extension_payload.range_class == ScalarRangeClass.OVER
    assert result.extension_payload.lut_index == 255


def test_query_transformed_point_returns_inverse_payload():
    """S027 transformed query reports source, declared, data, panel, and transform identity."""
    points = PointVisual(
        id="visual:points",
        positions=np.array([[1.0, 2.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([4.0], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
        transform=VisualTransformBinding.inline_affine(
            np.array([[1.0, 0.0, 2.0], [0.0, 1.0, -1.0], [0.0, 0.0, 1.0]])
        ),
    )
    view = View2D(
        id="view:main",
        panel_id="panel:main",
        x_range=(0.0, 6.0),
        y_range=(0.0, 2.0),
    )

    result = query_visuals(
        QueryRequest(id="query:points", panel_id="panel:main", coordinate=(3.0, 1.0)),
        [QueryVisualEntry(points)],
        view=view,
    )

    assert result.status == QueryStatus.HIT
    assert result.extension_payload_kind == TRANSFORM_QUERY_PAYLOAD_KIND
    assert isinstance(result.extension_payload, TransformQueryPayload)
    assert result.extension_payload.declared_space_coord == (3.0, 1.0)
    assert result.extension_payload.source_coord == (1.0, 2.0)
    assert result.extension_payload.data_coord == (3.0, 1.0)
    assert result.extension_payload.panel_ndc == (0.0, 0.0)
    assert result.extension_payload.view_id == "view:main"
    assert result.extension_payload.inline_transform_digest is not None


def test_query_transformed_ndc_point_reports_no_data_coordinate():
    """NDC visuals skip View2D and report data_coord as not applicable."""
    points = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([4.0], dtype=np.float32),
        coordinate_space=CoordinateSpace.NDC,
        transform=VisualTransformBinding.inline_affine(
            np.array([[1.0, 0.0, 0.25], [0.0, 1.0, -0.5], [0.0, 0.0, 1.0]])
        ),
    )

    result = query_visuals(
        QueryRequest(
            id="query:points", panel_id="panel:main", coordinate=(0.25, -0.5)
        ),
        [QueryVisualEntry(points)],
        view=View2D(id="view:main", panel_id="panel:main", x_range=(10.0, 20.0)),
    )

    assert result.status == QueryStatus.HIT
    assert result.extension_payload_kind == TRANSFORM_QUERY_PAYLOAD_KIND
    assert isinstance(result.extension_payload, TransformQueryPayload)
    assert result.extension_payload.panel_ndc == (0.25, -0.5)
    assert result.extension_payload.data_coord is None


def test_query_scalar_marker_returns_fill_color_payload():
    """Marker scalar fill query uses the fill slot and marker item identity."""
    scale = _test_color_scale(colormap_id=ColorMapId.GRAY)
    markers = MarkerVisual(
        id="visual:markers",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        shape=MarkerShape.SQUARE,
        sizes=np.array([4.0], dtype=np.float32),
        fill_color_encoding=ScalarColorEncoding(
            slot=ScalarColorSlot.FILL,
            values=np.array([0.25], dtype=np.float32),
            color_scale_id=scale.id,
            alpha=0.5,
        ),
    )

    result = query_visuals(
        QueryRequest(id="query:markers", panel_id="panel:main", coordinate=(0.0, 0.0)),
        [QueryVisualEntry(markers)],
        color_scales={scale.id: scale},
    )

    mapped = map_scalar_value(0.25, scale, alpha=0.5)
    assert result.status == QueryStatus.HIT
    assert result.visual_family == "marker"
    assert result.item_id == 0
    assert result.displayed_rgba == mapped.displayed_rgba
    assert result.extension_payload_kind == SCALAR_COLOR_QUERY_PAYLOAD_KIND
    assert result.extension_payload.color_slot == ScalarColorSlot.FILL
    assert result.extension_payload.item_kind == "marker"


def test_query_returns_text_item_payload_without_glyph_fields():
    """TextVisual query is item-level and reports public visual/item identity."""
    text = TextVisual(
        id="visual:text",
        texts=("first", "second"),
        positions=np.array([[0.0, 0.0], [10.0, 0.0]], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
        rgba=np.array([[255, 0, 0, 255], [0, 0, 255, 128]], dtype=np.uint8),
        font_size_px=np.array([4.0, 4.0], dtype=np.float32),
    )

    result = query_visuals(
        QueryRequest(id="query:text", panel_id="panel:main", coordinate=(10.5, 0.0)),
        [QueryVisualEntry(text)],
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_family == VisualFamily.TEXT
    assert result.visual_id == "visual:text"
    assert result.item_id == 1
    assert result.value == "second"
    assert result.extension_payload_kind == TEXT_QUERY_PAYLOAD_KIND
    assert result.extension_payload == {
        "kind": "text",
        "visual_id": "visual:text",
        "item_index": 1,
        "text": "second",
        "position": (10.0, 0.0),
        "coordinate_space": "data",
    }
    assert "glyph" not in result.extension_payload
    assert result.displayed_rgba == (0.0, 0.0, 1.0, 128 / 255.0)


def test_query_returns_mesh_face_payload():
    """MeshVisual query is face-level and reports public topology identity."""
    mesh = MeshVisual(
        id="visual:mesh",
        positions=np.array(
            [[-1.0, -1.0], [1.0, -1.0], [1.0, 1.0], [-1.0, 1.0]],
            dtype=np.float32,
        ),
        faces=np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([[255, 0, 0, 255], [0, 0, 255, 128]], dtype=np.uint8),
        color_mode=MeshColorMode.FACE,
    )

    result = query_visuals(
        QueryRequest(id="query:mesh", panel_id="panel:main", coordinate=(-0.5, 0.5)),
        [QueryVisualEntry(mesh)],
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_family == VisualFamily.MESH
    assert result.visual_id == "visual:mesh"
    assert result.item_id == 1
    assert result.displayed_rgba == (0.0, 0.0, 1.0, 128 / 255.0)
    assert result.value == {
        "hit_kind": "face",
        "face_index": 1,
        "vertex_indices": (0, 2, 3),
    }
    assert result.extension_payload_kind == MESH_QUERY_PAYLOAD_KIND
    assert result.extension_payload == MeshQueryPayload(
        visual_id="visual:mesh",
        hit_kind="face",
        face_index=1,
        vertex_indices=(0, 2, 3),
        panel_xy=(-0.5, 0.5),
        coordinate_space="data",
        displayed_rgba=(0.0, 0.0, 1.0, 128 / 255.0),
    )


def test_query_returns_uniform_mesh_color_and_frontmost_order():
    mesh = MeshVisual(
        id="visual:mesh",
        positions=np.array([[-1.0, -1.0], [1.0, -1.0], [0.0, 1.0]], dtype=np.float32),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([0, 255, 0, 255], dtype=np.uint8),
    )
    points = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([4.0], dtype=np.float32),
    )

    result = query_visuals(
        QueryRequest(
            id="query:mesh-all",
            panel_id="panel:main",
            coordinate=(0.0, 0.0),
            hit_policy=QueryHitPolicy.ALL,
        ),
        [QueryVisualEntry(mesh, z_order=0), QueryVisualEntry(points, z_order=2)],
    )

    assert result.status == QueryStatus.HIT
    assert [hit.visual_family for hit in result.hits] == [
        VisualFamily.POINT,
        VisualFamily.MESH,
    ]
    assert result.hits[1].displayed_rgba == (0.0, 1.0, 0.0, 1.0)


def test_query_defers_vertex_colored_mesh_readback():
    mesh = MeshVisual(
        id="visual:mesh",
        positions=np.array([[-1.0, -1.0], [1.0, -1.0], [0.0, 1.0]], dtype=np.float32),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array(
            [[255, 0, 0, 255], [0, 255, 0, 255], [0, 0, 255, 255]], dtype=np.uint8
        ),
        color_mode=MeshColorMode.VERTEX,
    )

    result = query_visuals(
        QueryRequest(
            id="query:mesh-vertex", panel_id="panel:main", coordinate=(0.0, 0.0)
        ),
        [QueryVisualEntry(mesh)],
    )

    assert result.status == QueryStatus.MISS


def test_query_returns_frontmost_text_over_point():
    """Text participates in item-level frontmost/all ordering."""
    points = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([4.0], dtype=np.float32),
    )
    text = TextVisual(
        id="visual:text",
        texts=("label",),
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
        font_size_px=4.0,
    )

    result = query_visuals(
        QueryRequest(
            id="query:front-text", panel_id="panel:main", coordinate=(0.0, 0.0)
        ),
        [QueryVisualEntry(points, z_order=0), QueryVisualEntry(text, z_order=2)],
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_family == VisualFamily.TEXT
    assert result.item_id == 0


def test_query_text_misses_outside_anchor_neighborhood():
    text = TextVisual(
        id="visual:text",
        texts=("label",),
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
        font_size_px=2.0,
    )

    result = query_visuals(
        QueryRequest(
            id="query:text-miss", panel_id="panel:main", coordinate=(20.0, 0.0)
        ),
        [QueryVisualEntry(text)],
    )

    assert result.status == QueryStatus.MISS


def test_query_request_defaults_to_data_scope():
    request = QueryRequest(
        id="query:default-scope", panel_id="panel:main", coordinate=(0.0, 0.0)
    )

    assert request.scope == QueryScope.DATA
    assert request.requested_extension_payload_kinds == ()


def test_query_result_with_hits_mirrors_first_hit_to_compatibility_fields():
    hit = QueryHit(
        contribution_kind=QueryContributionKind.DATA,
        visual_id="visual:points",
        visual_family=VisualFamily.POINT,
        item_id=2,
        visual_coordinate=(0.1, 0.2),
        data_coordinate=(0.1, 0.2),
        displayed_rgba=(0.0, 1.0, 0.0, 1.0),
    )

    result = QueryResult(
        request_id="query:hit-list",
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=(0.1, 0.2),
        hits=(hit,),
    )

    assert result.visual_id == "visual:points"
    assert result.visual_family == VisualFamily.POINT
    assert result.item_id == 2
    assert result.displayed_rgba == (0.0, 1.0, 0.0, 1.0)


def test_query_result_can_represent_all_hits_front_to_back():
    back = QueryHit(
        contribution_kind=QueryContributionKind.DATA,
        visual_id="visual:image",
        visual_family=VisualFamily.IMAGE,
    )
    front = QueryHit(
        contribution_kind=QueryContributionKind.DATA,
        visual_id="visual:points",
        visual_family=VisualFamily.POINT,
    )

    result = QueryResult(
        request_id="query:all",
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=(0.0, 0.0),
        hits=(front, back),
    )

    assert result.hits == (front, back)
    assert result.visual_id == "visual:points"
    assert result.visual_family == VisualFamily.POINT


def test_non_hit_query_results_reject_hit_payload_fields():
    with pytest.raises(ValueError, match="non-hit query results"):
        QueryResult(
            request_id="query:bad-miss",
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=(0.0, 0.0),
            hits=(
                QueryHit(
                    contribution_kind=QueryContributionKind.DATA,
                    visual_id="visual:points",
                ),
            ),
        )


def test_query_returns_miss_when_no_visual_contains_coordinate():
    """Miss is distinct from unsupported capability."""
    points = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([0.01], dtype=np.float32),
    )

    result = query_visuals(
        QueryRequest(id="query:miss", panel_id="panel:main", coordinate=(10.0, 10.0)),
        [QueryVisualEntry(points)],
    )

    assert result.status == QueryStatus.MISS
    assert not result.hit
    assert result.visual_id is None


def test_query_returns_outside_panel_before_testing_visuals():
    """Panel bounds produce outside-panel rather than miss."""
    points = PointVisual(
        id="visual:points",
        positions=np.array([[10.0, 10.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([100.0], dtype=np.float32),
    )

    result = query_visuals(
        QueryRequest(
            id="query:outside", panel_id="panel:main", coordinate=(10.0, 10.0)
        ),
        [QueryVisualEntry(points)],
        panel_bounds=(-1.0, 1.0, -1.0, 1.0),
    )

    assert result.status == QueryStatus.OUTSIDE_PANEL
    assert not result.hit
    assert result.visual_id is None


def test_query_helper_results_use_diagnostics_for_terminal_failures():
    """Unsupported and failed are distinct non-hit terminal statuses."""
    request = QueryRequest(
        id="query:unsupported", panel_id="panel:main", coordinate=(0.0, 0.0)
    )

    unsupported = unsupported_query_result(
        request, "backend does not advertise point-item queries"
    )
    failed = failed_query_result(request, "readback buffer allocation failed")

    assert unsupported.status == QueryStatus.UNSUPPORTED
    assert unsupported.diagnostic == "backend does not advertise point-item queries"
    assert failed.status == QueryStatus.FAILED
    assert failed.diagnostic == "readback buffer allocation failed"


def _test_color_scale(*, colormap_id: ColorMapId = ColorMapId.VIRIDIS) -> ColorScale:
    return ColorScale(
        id="scale:main",
        colormap=ColorMapRef(colormap_id),
        normalize=LinearNormalize(vmin=0.0, vmax=1.0),
    )
