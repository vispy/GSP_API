"""Tests for MeshTexturedMaterial construction and sanity checks."""

import numpy as np
import pytest

from gsp.constants import Constants
from gsp.core.texture import Texture
from gsp.materials.mesh_textured_material import MeshTexturedMaterial
from gsp.types.buffer_type import BufferType
from gsp_matplotlib.extra.bufferx import Bufferx


def _make_texture(width: int = 4, height: int = 4) -> Texture:
    pixels = np.full((width * height, 4), 255, dtype=np.uint8)
    buffer = Bufferx.from_numpy(pixels, BufferType.rgba8)
    return Texture(buffer, width, height)


def _make_rgba8_buffer(rgba: tuple[int, int, int, int] = (255, 255, 255, 255)):
    return Bufferx.from_numpy(np.array([list(rgba)], dtype=np.uint8), BufferType.rgba8)


class TestMeshTexturedMaterial:
    """Construction and sanity-check tests for MeshTexturedMaterial."""

    def test_construct_valid(self):
        """A material built with rgba8 buffers and a valid Texture passes check_attributes_buffer."""
        material = MeshTexturedMaterial(
            texture=_make_texture(4, 4),
            color=_make_rgba8_buffer(),
            specular_color=_make_rgba8_buffer(),
            shininess=32.0,
            lights=[],
            face_sorting=True,
            face_culling=Constants.FaceCulling.FrontSide,
        )
        material.check_attributes_buffer()

        assert material.get_shininess() == 32.0
        assert material.get_face_sorting() is True
        assert material.get_face_culling() == Constants.FaceCulling.FrontSide
        assert material.get_texture().get_width() == 4
        assert material.get_texture().get_height() == 4

    def test_non_rgba8_color_raises(self):
        """A non-rgba8 color buffer triggers an AssertionError in check_attributes_buffer."""
        bad_color = Bufferx.from_numpy(np.array([[1.0, 1.0, 1.0]], dtype=np.float32), BufferType.vec3)
        material = MeshTexturedMaterial(
            texture=_make_texture(),
            color=bad_color,
            specular_color=_make_rgba8_buffer(),
            shininess=32.0,
            lights=[],
            face_sorting=True,
            face_culling=Constants.FaceCulling.FrontSide,
        )
        with pytest.raises(AssertionError, match="color buffer must be rgba8"):
            material.check_attributes_buffer()

    def test_texture_size_mismatch_raises(self):
        """A texture whose buffer length doesn't match width * height triggers an AssertionError."""
        pixels = np.full((4 * 4, 4), 255, dtype=np.uint8)
        buffer = Bufferx.from_numpy(pixels, BufferType.rgba8)
        texture = Texture(buffer, 8, 8)  # claims 64 pixels but buffer has 16

        material = MeshTexturedMaterial(
            texture=texture,
            color=_make_rgba8_buffer(),
            specular_color=_make_rgba8_buffer(),
            shininess=32.0,
            lights=[],
            face_sorting=True,
            face_culling=Constants.FaceCulling.FrontSide,
        )
        with pytest.raises(AssertionError, match="does not match width \\* height"):
            material.check_attributes_buffer()
