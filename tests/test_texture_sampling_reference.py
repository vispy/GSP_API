"""Numeric fixtures for the S059 Texture2D filtering contract."""

import numpy as np

from gsp.protocol import TextureFilter
from gsp.qa.visual.texture_reference import (
    multiply_texture_rgba,
    sample_texture2d_rgba8,
)


TEXTURE = np.array(
    [
        [[255, 0, 0, 255], [0, 255, 0, 128]],
        [[0, 0, 255, 64], [255, 255, 255, 0]],
    ],
    dtype=np.uint8,
)


def test_texel_centers_pin_orientation_for_both_filters():
    centers = np.array(
        [[0.25, 0.75], [0.75, 0.75], [0.25, 0.25], [0.75, 0.25]],
        dtype=np.float64,
    )
    expected = TEXTURE.reshape(4, 4).astype(np.float64) / 255.0

    for texture_filter in TextureFilter:
        np.testing.assert_allclose(
            sample_texture2d_rgba8(TEXTURE, centers, texture_filter=texture_filter),
            expected,
        )


def test_linear_interpolation_and_clamp_to_edge():
    probes = np.array(
        [
            [0.5, 0.5],
            [-1.0, 0.75],
            [2.0, 0.25],
            [0.0, 1.0],
            [1.0, 0.0],
        ],
        dtype=np.float64,
    )
    actual = sample_texture2d_rgba8(
        TEXTURE, probes, texture_filter=TextureFilter.LINEAR
    )
    expected_center = TEXTURE.astype(np.float64).mean(axis=(0, 1)) / 255.0

    np.testing.assert_allclose(actual[0], expected_center)
    np.testing.assert_allclose(actual[1], TEXTURE[0, 0] / 255.0)
    np.testing.assert_allclose(actual[2], TEXTURE[1, 1] / 255.0)
    np.testing.assert_allclose(actual[3], TEXTURE[0, 0] / 255.0)
    np.testing.assert_allclose(actual[4], TEXTURE[1, 1] / 255.0)


def test_linear_interpolates_straight_alpha_then_multiplies_base_rgba():
    sample = sample_texture2d_rgba8(
        TEXTURE,
        np.array([[0.5, 0.5]], dtype=np.float64),
        texture_filter=TextureFilter.LINEAR,
    )
    base = np.array([0.5, 0.25, 1.0, 0.5], dtype=np.float64)

    expected_sample = TEXTURE.astype(np.float64).mean(axis=(0, 1)) / 255.0
    np.testing.assert_allclose(sample[0], expected_sample)
    np.testing.assert_allclose(
        multiply_texture_rgba(sample, base)[0], expected_sample * base
    )


def test_shared_texture_can_produce_distinct_nearest_and_linear_samples():
    probe = np.array([[0.5, 0.5]], dtype=np.float64)
    nearest = sample_texture2d_rgba8(
        TEXTURE, probe, texture_filter=TextureFilter.NEAREST
    )
    linear = sample_texture2d_rgba8(TEXTURE, probe, texture_filter=TextureFilter.LINEAR)

    np.testing.assert_allclose(nearest[0], TEXTURE[1, 1] / 255.0)
    assert not np.allclose(nearest, linear)
