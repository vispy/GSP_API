"""Tests for the bounded Datoviz v0.4 protocol adapter slice."""

from __future__ import annotations

import numpy as np
import pytest

from gsp.protocol import ImageOrigin, ImageVisual, PointVisual
from gsp.protocol.visuals import CoordinateSpace, ImageInterpolation
from gsp_datoviz.protocol_renderer import (
    DatovizV04ProtocolRenderer,
    DatovizV04Unavailable,
    DatovizV04Unsupported,
    capability_snapshot,
    is_datoviz_v04_facade,
)


class FakeDatovizV04:
    """Small recorder for the dvz_* facade used by the adapter."""

    def __init__(self):
        self.calls = []
        self.destroyed = False

    def dvz_scene(self):
        self.calls.append(("scene",))
        return "scene"

    def dvz_figure(self, scene, width, height, flags):
        self.calls.append(("figure", scene, width, height, flags))
        return "figure"

    def dvz_panel_full(self, figure):
        self.calls.append(("panel_full", figure))
        return "panel"

    def dvz_point(self, scene, flags):
        self.calls.append(("point", scene, flags))
        return "point-visual"

    def dvz_image(self, scene, flags):
        self.calls.append(("image", scene, flags))
        return "image-visual"

    def dvz_visual_set_data(self, visual, name, data):
        self.calls.append(("set_data", visual, name, np.array(data, copy=True)))
        return 0

    def dvz_visual_set_texture(self, visual, pixels, width, height):
        self.calls.append(("set_texture", visual, np.array(pixels, copy=True), width, height))
        return 0

    def dvz_panel_add_visual(self, panel, visual, attach_desc):
        self.calls.append(("add_visual", panel, visual, attach_desc))
        return 0

    def dvz_scene_destroy(self, scene):
        self.calls.append(("destroy", scene))
        self.destroyed = True


def _calls(fake, name):
    return [call for call in fake.calls if call[0] == name]


def test_capability_snapshot_defers_query_support():
    caps = capability_snapshot()

    assert caps.server_name == "datoviz-v0.4-protocol-slice"
    assert caps.visual_families == ("point", "image")
    assert caps.texture_formats == ("rgba8",)
    assert caps.query_modes == ()
    assert caps.metadata["datoviz_api"] == "v0.4 dvz_* facade"


def test_facade_shape_rejects_missing_v04_functions():
    class IncompleteDatoviz:
        pass

    assert is_datoviz_v04_facade(IncompleteDatoviz()) is False

    with pytest.raises(DatovizV04Unavailable, match="missing v0.4 functions"):
        DatovizV04ProtocolRenderer(dvz=IncompleteDatoviz())


def test_add_point_visual_uses_dvz_point_attributes_and_diameter_pixels():
    fake = FakeDatovizV04()
    renderer = DatovizV04ProtocolRenderer(dvz=fake, width=320, height=240)
    visual = PointVisual(
        id="visual:points",
        positions=np.array([[-0.5, 0.25], [0.5, -0.25]], dtype=np.float32),
        colors=np.array([[1.0, 0.0, 0.0, 1.0], [0.0, 0.5, 1.0, 0.5]], dtype=np.float32),
        sizes=np.array([np.pi, 4.0 * np.pi], dtype=np.float32),
    )

    dvz_visual = renderer.add_point_visual(visual)

    assert dvz_visual == "point-visual"
    set_data = _calls(fake, "set_data")
    assert [call[2] for call in set_data] == ["position", "color", "diameter"]
    np.testing.assert_allclose(set_data[0][3], [[-0.5, 0.25, 0.0], [0.5, -0.25, 0.0]])
    np.testing.assert_array_equal(set_data[1][3], [[255, 0, 0, 255], [0, 128, 255, 128]])
    np.testing.assert_allclose(set_data[2][3], [2.0, 4.0], rtol=1e-6)
    assert _calls(fake, "add_visual")[-1] == ("add_visual", "panel", "point-visual", None)


def test_add_image_visual_uses_texture_convenience_path_and_origin_texcoords():
    fake = FakeDatovizV04()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    image = np.array(
        [
            [[255, 0, 0], [0, 255, 0]],
            [[0, 0, 255], [255, 255, 255]],
        ],
        dtype=np.uint8,
    )
    visual = ImageVisual(
        id="visual:image",
        image=image,
        extent=(-1.0, 1.0, -0.5, 0.5),
        origin=ImageOrigin.UPPER,
    )

    dvz_visual = renderer.add_image_visual(visual)

    assert dvz_visual == "image-visual"
    set_data = _calls(fake, "set_data")
    assert [call[2] for call in set_data] == ["position", "texcoords"]
    np.testing.assert_allclose(
        set_data[0][3],
        [[-1.0, -0.5, 0.0], [-1.0, 0.5, 0.0], [1.0, -0.5, 0.0], [1.0, 0.5, 0.0]],
    )
    np.testing.assert_allclose(set_data[1][3], [[0.0, 1.0], [0.0, 0.0], [1.0, 1.0], [1.0, 0.0]])

    texture_call = _calls(fake, "set_texture")[0]
    assert texture_call[3:] == (2, 2)
    assert texture_call[2].shape == (2, 2, 4)
    np.testing.assert_array_equal(texture_call[2][:, :, 3], 255)


def test_lower_origin_texcoords_are_not_flipped():
    fake = FakeDatovizV04()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    visual = ImageVisual(
        id="visual:image",
        image=np.zeros((1, 1, 4), dtype=np.uint8),
        extent=(0.0, 1.0, 0.0, 1.0),
        origin=ImageOrigin.LOWER,
    )

    renderer.add_image_visual(visual)

    texcoords = _calls(fake, "set_data")[1][3]
    np.testing.assert_allclose(texcoords, [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])


def test_image_slice_rejects_unlocked_semantics():
    fake = FakeDatovizV04()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    with pytest.raises(DatovizV04Unsupported, match="uint8 RGB/RGBA"):
        renderer.add_image_visual(
            ImageVisual(
                id="visual:float-image",
                image=np.zeros((2, 2), dtype=np.float32),
                extent=(0.0, 1.0, 0.0, 1.0),
            )
        )

    with pytest.raises(DatovizV04Unsupported, match="interpolation"):
        renderer.add_image_visual(
            ImageVisual(
                id="visual:linear-image",
                image=np.zeros((2, 2, 4), dtype=np.uint8),
                extent=(0.0, 1.0, 0.0, 1.0),
                interpolation=ImageInterpolation.LINEAR,
            )
        )

    with pytest.raises(DatovizV04Unsupported, match="NDC point"):
        renderer.add_point_visual(
            PointVisual(
                id="visual:data-points",
                positions=np.zeros((1, 2), dtype=np.float32),
                colors=np.zeros((1, 4), dtype=np.uint8),
                sizes=1.0,
                coordinate_space=CoordinateSpace.DATA,
            )
        )


def test_renderer_close_uses_scene_destroy_when_available():
    fake = FakeDatovizV04()

    with DatovizV04ProtocolRenderer(dvz=fake) as renderer:
        assert renderer.scene == "scene"

    assert fake.destroyed is True
    assert _calls(fake, "destroy") == [("destroy", "scene")]


def test_imported_datoviz_binding_has_expected_v04_shape_when_available():
    dvz = pytest.importorskip("datoviz")

    assert is_datoviz_v04_facade(dvz)
