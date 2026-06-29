"""Tests for physical canvas size policy resolution."""

import pytest

from gsp.protocol import (
    CanvasResolveExactness,
    CanvasSize,
    CanvasSizePolicy,
)


def test_pixel_exact_resolves_deterministic_framebuffer_size():
    resolved = CanvasSize.pixel_exact(1280, 720).resolve(device_scale=2.0)

    assert resolved.requested_size.policy is CanvasSizePolicy.PIXEL_EXACT
    assert resolved.canvas_width_px == 1280.0
    assert resolved.canvas_height_px == 720.0
    assert resolved.framebuffer_width == 1280
    assert resolved.framebuffer_height == 720
    assert resolved.host_logical_width == 640
    assert resolved.host_logical_height == 360
    assert resolved.framebuffer_per_canvas_px == 1.0
    assert resolved.exactness is CanvasResolveExactness.EXACT


def test_reference_px_uses_reference_dpi_for_physical_target():
    resolved = CanvasSize.reference_px(960, 540, reference_dpi=96).resolve(
        output_dpi=144,
        device_scale=1.5,
    )

    assert resolved.canvas_width_px == 960.0
    assert resolved.canvas_height_px == 540.0
    assert resolved.framebuffer_width == 1440
    assert resolved.framebuffer_height == 810
    assert resolved.host_logical_width == 960
    assert resolved.host_logical_height == 540
    assert resolved.framebuffer_per_canvas_px == 1.5
    assert resolved.canvas_px_to_points(20.0) == pytest.approx(15.0)
    assert resolved.target_width_mm == pytest.approx(254.0)


def test_physical_mm_derives_canvas_reference_pixels():
    resolved = CanvasSize.physical_mm(254.0, 127.0, reference_dpi=96).resolve(
        output_dpi=192
    )

    assert resolved.canvas_width_px == pytest.approx(960.0)
    assert resolved.canvas_height_px == pytest.approx(480.0)
    assert resolved.framebuffer_width == 1920
    assert resolved.framebuffer_height == 960
    assert resolved.framebuffer_per_canvas_px == 2.0


def test_invalid_canvas_size_values_are_rejected():
    with pytest.raises(ValueError, match="width"):
        CanvasSize.pixel_exact(0, 720)
    with pytest.raises(ValueError, match="reference_dpi"):
        CanvasSize.reference_px(1280, 720, reference_dpi=0)
    with pytest.raises(ValueError, match="requested_device_scale"):
        CanvasSize.pixel_exact(1280, 720).with_requested_device_scale(0)
