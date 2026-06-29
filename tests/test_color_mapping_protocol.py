"""Tests for the accepted S026 color mapping protocol model."""

import numpy as np
import pytest

from gsp.protocol import (
    ColorbarGuide,
    ColorbarGuideStyle,
    ColorbarOrientation,
    ColorbarPlacement,
    ColorMapId,
    ColorMapKind,
    ColorMapRef,
    ColorScale,
    CoordinateSpace,
    ImageVisual,
    LinearNormalize,
    MarkerShape,
    MarkerVisual,
    MeshVisual,
    NormalizeKind,
    PointVisual,
    ScalarColorDomain,
    ScalarColorEncoding,
    ScalarColorSlot,
)


def test_color_scale_accepts_named_colormap_and_linear_normalize():
    scale = ColorScale(
        id="scale:temperature",
        colormap=ColorMapRef(ColorMapId.VIRIDIS),
        normalize=LinearNormalize(vmin=-1.0, vmax=1.0),
        description="temperature",
    )

    assert scale.colormap.kind == ColorMapKind.NAMED
    assert scale.colormap.id == ColorMapId.VIRIDIS
    assert scale.normalize.kind == NormalizeKind.LINEAR
    assert scale.normalize.clip is True


def test_linear_normalize_rejects_invalid_limits_and_unclipped_mode():
    with pytest.raises(ValueError, match="less than"):
        LinearNormalize(vmin=1.0, vmax=1.0)

    with pytest.raises(ValueError, match="finite"):
        LinearNormalize(vmin=0.0, vmax=float("inf"))

    with pytest.raises(ValueError, match="clip=True"):
        LinearNormalize(vmin=0.0, vmax=1.0, clip=False)


def test_scalar_color_encoding_validates_values_alpha_and_ids():
    encoding = ScalarColorEncoding(
        slot=ScalarColorSlot.COLOR,
        values=np.array([0.0, 0.5, 1.0], dtype=np.float32),
        color_scale_id="scale:main",
        alpha=0.75,
        domain=ScalarColorDomain.ITEM,
    )

    assert encoding.slot == ScalarColorSlot.COLOR
    assert encoding.values.dtype == np.dtype(np.float32)
    assert encoding.alpha == 0.75

    with pytest.raises(ValueError, match="finite"):
        ScalarColorEncoding(
            slot=ScalarColorSlot.COLOR,
            values=np.array([0.0, np.nan], dtype=np.float32),
            color_scale_id="scale:main",
        )

    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        ScalarColorEncoding(
            slot=ScalarColorSlot.COLOR,
            values=np.array([0.0], dtype=np.float32),
            color_scale_id="scale:main",
            alpha=2.0,
        )


def test_colorbar_guide_accepts_explicit_ticks_and_defaults_placement():
    guide = ColorbarGuide(
        id="guide:colorbar",
        panel_id="panel:main",
        color_scale_id="scale:main",
        linked_visual_ids=("visual:image",),
        label="intensity",
        ticks=(0.0, 0.5, 1.0),
        tick_labels=("low", "mid", "high"),
    )

    assert guide.orientation == ColorbarOrientation.VERTICAL
    assert guide.placement == ColorbarPlacement.RIGHT
    assert guide.style.ramp_width_px == 36.0


def test_colorbar_guide_style_validates_positive_canvas_pixel_values():
    style = ColorbarGuideStyle(
        ramp_width_px=42.0,
        tick_length_px=7.0,
        label_gap_px=8.0,
        min_length_px=180.0,
        length_fraction=0.75,
    )

    assert style.ramp_width_px == 42.0
    assert style.length_fraction == 0.75

    with pytest.raises(ValueError, match="ramp_width_px"):
        ColorbarGuideStyle(ramp_width_px=0.0)
    with pytest.raises(ValueError, match="length_fraction"):
        ColorbarGuideStyle(length_fraction=1.5)


def test_colorbar_guide_rejects_bad_tick_labels_and_placement():
    with pytest.raises(ValueError, match="tick_labels length"):
        ColorbarGuide(
            id="guide:colorbar",
            panel_id="panel:main",
            color_scale_id="scale:main",
            ticks=(0.0, 1.0),
            tick_labels=("low",),
        )

    with pytest.raises(ValueError, match="vertical"):
        ColorbarGuide(
            id="guide:colorbar",
            panel_id="panel:main",
            color_scale_id="scale:main",
            placement=ColorbarPlacement.BOTTOM,
        )


def test_scalar_image_accepts_color_scale_id_and_rejects_rgb_color_scale():
    image = ImageVisual(
        id="visual:image",
        image=np.array([[0.0, 1.0]], dtype=np.float32),
        extent=(0.0, 1.0, 0.0, 1.0),
        color_scale_id="scale:image",
    )

    assert image.color_scale_id == "scale:image"

    with pytest.raises(ValueError, match="scalar images"):
        ImageVisual(
            id="visual:rgb",
            image=np.zeros((1, 1, 3), dtype=np.float32),
            extent=(0.0, 1.0, 0.0, 1.0),
            color_scale_id="scale:image",
        )


def test_point_visual_accepts_scalar_color_encoding_instead_of_rgba():
    visual = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32),
        sizes=np.array([4.0, 6.0], dtype=np.float32),
        color_encoding=ScalarColorEncoding(
            slot=ScalarColorSlot.COLOR,
            values=np.array([0.0, 1.0], dtype=np.float32),
            color_scale_id="scale:points",
        ),
    )

    assert visual.colors is None
    assert visual.color_encoding is not None


def test_point_visual_rejects_rgba_and_scalar_encoding_conflict():
    with pytest.raises(ValueError, match="mutually exclusive"):
        PointVisual(
            id="visual:points",
            positions=np.array([[0.0, 0.0]], dtype=np.float32),
            colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
            sizes=4.0,
            color_encoding=ScalarColorEncoding(
                slot=ScalarColorSlot.COLOR,
                values=np.array([0.0], dtype=np.float32),
                color_scale_id="scale:points",
            ),
        )


def test_marker_visual_accepts_fill_scalar_encoding_and_preserves_stroke_rgba():
    visual = MarkerVisual(
        id="visual:markers",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        shape=MarkerShape.DISC,
        sizes=8.0,
        fill_color_encoding=ScalarColorEncoding(
            slot=ScalarColorSlot.FILL,
            values=np.array([0.5], dtype=np.float32),
            color_scale_id="scale:markers",
        ),
        stroke_color=np.array([0, 0, 0, 255], dtype=np.uint8),
    )

    assert visual.fill_colors is None
    assert visual.fill_color_encoding is not None


def test_scalar_encoding_shape_and_slot_are_validated_by_visuals():
    with pytest.raises(ValueError, match="shape"):
        PointVisual(
            id="visual:points",
            positions=np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32),
            sizes=4.0,
            color_encoding=ScalarColorEncoding(
                slot=ScalarColorSlot.COLOR,
                values=np.array([0.0], dtype=np.float32),
                color_scale_id="scale:points",
            ),
        )

    with pytest.raises(ValueError, match="slot"):
        MarkerVisual(
            id="visual:markers",
            positions=np.array([[0.0, 0.0]], dtype=np.float32),
            shape=MarkerShape.DISC,
            sizes=8.0,
            fill_color_encoding=ScalarColorEncoding(
                slot=ScalarColorSlot.COLOR,
                values=np.array([0.5], dtype=np.float32),
                color_scale_id="scale:markers",
            ),
        )


def test_mesh_visual_accepts_capability_gated_face_scalar_encoding():
    visual = MeshVisual(
        id="visual:mesh",
        positions=np.array([[-0.5, -0.5], [0.5, -0.5], [0.0, 0.5]], dtype=np.float32),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        face_color_encoding=ScalarColorEncoding(
            slot=ScalarColorSlot.FACE_COLOR,
            values=np.array([0.25], dtype=np.float32),
            color_scale_id="scale:mesh",
            domain=ScalarColorDomain.FACE,
        ),
    )

    assert visual.color is None
    assert visual.face_color_encoding is not None


def test_mesh_visual_rejects_face_scalar_encoding_conflicts():
    with pytest.raises(ValueError, match="mutually exclusive"):
        MeshVisual(
            id="visual:mesh",
            positions=np.array(
                [[-0.5, -0.5], [0.5, -0.5], [0.0, 0.5]], dtype=np.float32
            ),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.DATA,
            color=np.array([255, 0, 0, 255], dtype=np.uint8),
            face_color_encoding=ScalarColorEncoding(
                slot=ScalarColorSlot.FACE_COLOR,
                values=np.array([0.25], dtype=np.float32),
                color_scale_id="scale:mesh",
            ),
        )
