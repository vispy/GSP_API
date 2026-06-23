"""S023 visual QA case registry."""

from __future__ import annotations

import numpy as np

from gsp.protocol import CoordinateSpace, ImageInterpolation, ImageOrigin, ImageVisual, MarkerShape, MarkerVisual, PointVisual
from gsp.qa.visual.case_spec import VisualQACase, VisualQAScene


S023_SUITE = "s023"


def list_cases(*, suite: str = S023_SUITE) -> tuple[VisualQACase, ...]:
    """Return the registered cases for a suite."""
    if suite != S023_SUITE:
        raise ValueError(f"unknown visual QA suite: {suite}")
    return (
        VisualQACase(
            case_id="point/basic_ndc",
            title="Basic NDC point visual",
            family="point",
            required_features=("point", "ndc", "rgba8", "pixel-size"),
            builder=_point_basic_ndc,
        ),
        VisualQACase(
            case_id="point/diameter_ramp_ndc",
            title="Point diameter ramp in NDC",
            family="point",
            required_features=("point", "ndc", "rgba8", "diameter-ramp"),
            builder=_point_diameter_ramp_ndc,
        ),
        VisualQACase(
            case_id="point/alpha_overlap_ndc",
            title="Point alpha overlap in NDC",
            family="point",
            required_features=("point", "ndc", "rgba8", "alpha"),
            builder=_point_alpha_overlap_ndc,
        ),
        VisualQACase(
            case_id="marker/shapes_ndc",
            title="Marker built-in shapes in NDC",
            family="marker",
            required_features=("marker", "ndc", "rgba8", "shape", "stroke"),
            builder=_marker_shapes_ndc,
        ),
        VisualQACase(
            case_id="marker/angle_size_stroke_ndc",
            title="Marker angle, size, and stroke in NDC",
            family="marker",
            required_features=("marker", "ndc", "rgba8", "angle", "pixel-size", "stroke"),
            builder=_marker_angle_size_stroke_ndc,
        ),
        VisualQACase(
            case_id="image/checker_nearest_ndc",
            title="Nearest checker image in NDC",
            family="image",
            required_features=("image", "ndc", "rgba8", "nearest", "extent"),
            builder=_image_checker_nearest_ndc,
        ),
        VisualQACase(
            case_id="overlay/point_over_image_ndc",
            title="Point over image overlay in NDC",
            family="overlay",
            required_features=("point", "image", "ndc", "rgba8", "layering"),
            builder=_overlay_point_over_image_ndc,
        ),
    )


def get_case(case_id: str, *, suite: str = S023_SUITE) -> VisualQACase:
    """Return one registered case by id."""
    for case in list_cases(suite=suite):
        if case.case_id == case_id:
            return case
    raise ValueError(f"unknown visual QA case: {case_id}")


def case_slug(case_id: str) -> str:
    """Return a filesystem-safe case slug."""
    return case_id.replace("/", "_")


def _point_basic_ndc() -> VisualQAScene:
    positions = np.array(
        [
            [-0.75, -0.55],
            [-0.35, 0.35],
            [0.0, 0.0],
            [0.38, -0.25],
            [0.75, 0.55],
        ],
        dtype=np.float32,
    )
    colors = np.array(
        [
            [230, 57, 70, 255],
            [42, 157, 143, 255],
            [38, 70, 83, 255],
            [244, 162, 97, 255],
            [69, 123, 157, 255],
        ],
        dtype=np.uint8,
    )
    sizes = np.full(positions.shape[0], 18.0, dtype=np.float32)
    visual = PointVisual(
        id="visual:point-basic-ndc",
        positions=positions,
        colors=colors,
        sizes=sizes,
        coordinate_space=CoordinateSpace.NDC,
    )
    return VisualQAScene(
        case_id="point/basic_ndc",
        visuals=(visual,),
        arrays={"point_positions": positions, "point_colors": colors, "point_sizes": sizes},
        notes=("Five colored NDC points with a constant nominal pixel size.",),
    )


def _point_diameter_ramp_ndc() -> VisualQAScene:
    diameters = np.array([4.0, 8.0, 12.0, 18.0, 26.0, 36.0], dtype=np.float32)
    positions = np.column_stack(
        (
            np.linspace(-0.75, 0.75, diameters.shape[0], dtype=np.float32),
            np.zeros(diameters.shape[0], dtype=np.float32),
        )
    ).astype(np.float32)
    colors = np.array(
        [
            [33, 102, 172, 255],
            [67, 147, 195, 255],
            [146, 197, 222, 255],
            [244, 165, 130, 255],
            [214, 96, 77, 255],
            [178, 24, 43, 255],
        ],
        dtype=np.uint8,
    )
    visual = PointVisual(
        id="visual:point-diameter-ramp-ndc",
        positions=positions,
        colors=colors,
        sizes=diameters,
        coordinate_space=CoordinateSpace.NDC,
    )
    return VisualQAScene(
        case_id="point/diameter_ramp_ndc",
        visuals=(visual,),
        arrays={"point_positions": positions, "point_colors": colors, "point_diameters": diameters},
        notes=("Horizontal point row with increasing requested pixel diameters.",),
    )


def _point_alpha_overlap_ndc() -> VisualQAScene:
    positions = np.array(
        [
            [-0.11, 0.0],
            [0.0, 0.0],
            [0.11, 0.0],
        ],
        dtype=np.float32,
    )
    colors = np.array(
        [
            [230, 57, 70, 160],
            [42, 157, 143, 160],
            [38, 70, 83, 160],
        ],
        dtype=np.uint8,
    )
    sizes = np.full(positions.shape[0], 86.0, dtype=np.float32)
    visual = PointVisual(
        id="visual:point-alpha-overlap-ndc",
        positions=positions,
        colors=colors,
        sizes=sizes,
        coordinate_space=CoordinateSpace.NDC,
    )
    return VisualQAScene(
        case_id="point/alpha_overlap_ndc",
        visuals=(visual,),
        arrays={"point_positions": positions, "point_colors": colors, "point_sizes": sizes},
        notes=("Three strongly overlapping semi-transparent points with fixed pixel diameters.",),
    )


def _marker_shapes_ndc() -> VisualQAScene:
    positions = np.array(
        [
            [-0.72, 0.0],
            [-0.36, 0.0],
            [0.0, 0.0],
            [0.36, 0.0],
            [0.72, 0.0],
        ],
        dtype=np.float32,
    )
    shapes = (
        MarkerShape.DISC,
        MarkerShape.SQUARE,
        MarkerShape.TRIANGLE,
        MarkerShape.DIAMOND,
        MarkerShape.CROSS,
    )
    colors = np.array(
        [
            [216, 27, 96, 255],
            [30, 136, 229, 255],
            [0, 137, 123, 255],
            [251, 140, 0, 255],
            [94, 53, 177, 255],
        ],
        dtype=np.uint8,
    )
    sizes = np.full(positions.shape[0], 42.0, dtype=np.float32)
    shape_codes = np.arange(len(shapes), dtype=np.uint8)
    visual = MarkerVisual(
        id="visual:marker-shapes-ndc",
        positions=positions,
        shape=shapes,
        fill_colors=colors,
        sizes=sizes,
        stroke_color=np.array([16, 16, 16, 255], dtype=np.uint8),
        stroke_width=4.0,
        coordinate_space=CoordinateSpace.NDC,
    )
    return VisualQAScene(
        case_id="marker/shapes_ndc",
        visuals=(visual,),
        arrays={
            "marker_positions": positions,
            "marker_shape_codes": shape_codes,
            "marker_fill_colors": colors,
            "marker_sizes": sizes,
        },
        notes=("Five conservative built-in marker shapes with shared dark pixel-width stroke.",),
    )


def _marker_angle_size_stroke_ndc() -> VisualQAScene:
    count = 6
    positions = np.column_stack(
        (
            np.linspace(-0.72, 0.72, count, dtype=np.float32),
            np.zeros(count, dtype=np.float32),
        )
    ).astype(np.float32)
    sizes = np.array([18.0, 24.0, 30.0, 36.0, 44.0, 54.0], dtype=np.float32)
    angles = np.linspace(0.0, np.pi * 0.9, count, dtype=np.float32)
    colors = np.array(
        [
            [46, 125, 50, 255],
            [67, 160, 71, 255],
            [124, 179, 66, 255],
            [251, 192, 45, 255],
            [245, 124, 0, 255],
            [198, 40, 40, 255],
        ],
        dtype=np.uint8,
    )
    visual = MarkerVisual(
        id="visual:marker-angle-size-stroke-ndc",
        positions=positions,
        shape=MarkerShape.TRIANGLE,
        fill_colors=colors,
        sizes=sizes,
        angle=angles,
        stroke_color=np.array([16, 16, 16, 255], dtype=np.uint8),
        stroke_width=4.0,
        coordinate_space=CoordinateSpace.NDC,
    )
    return VisualQAScene(
        case_id="marker/angle_size_stroke_ndc",
        visuals=(visual,),
        arrays={
            "marker_positions": positions,
            "marker_fill_colors": colors,
            "marker_sizes": sizes,
            "marker_angles": angles,
        },
        notes=("Rotating triangle markers with increasing requested pixel diameters and a visible stroke.",),
    )


def _image_checker_nearest_ndc() -> VisualQAScene:
    image = _checker_image(8)
    visual = ImageVisual(
        id="visual:image-checker-nearest-ndc",
        image=image,
        extent=(-0.75, 0.75, -0.55, 0.55),
        coordinate_space=CoordinateSpace.NDC,
        interpolation=ImageInterpolation.NEAREST,
        origin=ImageOrigin.UPPER,
    )
    return VisualQAScene(
        case_id="image/checker_nearest_ndc",
        visuals=(visual,),
        arrays={"checker_rgba": image},
        notes=("Small RGBA checkerboard with nearest interpolation and explicit NDC extent.",),
    )


def _overlay_point_over_image_ndc() -> VisualQAScene:
    image = _checker_image(10)
    image_visual = ImageVisual(
        id="visual:overlay-checker-image-ndc",
        image=image,
        extent=(-0.85, 0.85, -0.65, 0.65),
        coordinate_space=CoordinateSpace.NDC,
        interpolation=ImageInterpolation.NEAREST,
        origin=ImageOrigin.UPPER,
    )
    positions = np.array([[-0.45, -0.25], [0.0, 0.0], [0.45, 0.25]], dtype=np.float32)
    colors = np.array([[255, 255, 255, 240], [230, 57, 70, 255], [29, 53, 87, 240]], dtype=np.uint8)
    sizes = np.array([18.0, 28.0, 18.0], dtype=np.float32)
    point_visual = PointVisual(
        id="visual:overlay-points-ndc",
        positions=positions,
        colors=colors,
        sizes=sizes,
        coordinate_space=CoordinateSpace.NDC,
    )
    return VisualQAScene(
        case_id="overlay/point_over_image_ndc",
        visuals=(image_visual, point_visual),
        arrays={
            "checker_rgba": image,
            "point_positions": positions,
            "point_colors": colors,
            "point_sizes": sizes,
        },
        notes=("Checker image with three points rendered over the image.",),
    )


def _checker_image(size: int) -> np.ndarray:
    grid = np.indices((size, size)).sum(axis=0) % 2
    image = np.zeros((size, size, 4), dtype=np.uint8)
    image[grid == 0] = np.array([245, 245, 245, 255], dtype=np.uint8)
    image[grid == 1] = np.array([35, 40, 45, 255], dtype=np.uint8)
    return image
