"""S023 visual QA case registry."""

from __future__ import annotations

import numpy as np

from gsp.protocol import (
    CoordinateSpace,
    ImageInterpolation,
    ImageOrigin,
    ImageVisual,
    MarkerShape,
    MarkerVisual,
    PathVisual,
    PointVisual,
    SegmentVisual,
    StrokeCap,
    StrokeJoin,
)
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
            required_features=(
                "marker",
                "ndc",
                "rgba8",
                "angle",
                "pixel-size",
                "stroke",
            ),
            builder=_marker_angle_size_stroke_ndc,
        ),
        VisualQACase(
            case_id="segment/width_cap_ndc",
            title="Segment width and cap styles in NDC",
            family="segment",
            required_features=("segment", "ndc", "rgba8", "width", "cap"),
            builder=_segment_width_cap_ndc,
        ),
        VisualQACase(
            case_id="segment/alpha_order_ndc",
            title="Segment alpha and draw order in NDC",
            family="segment",
            required_features=("segment", "ndc", "rgba8", "alpha", "layering"),
            builder=_segment_alpha_order_ndc,
        ),
        VisualQACase(
            case_id="path/subpaths_width_join_ndc",
            title="Path subpaths, widths, caps, and joins in NDC",
            family="path",
            required_features=(
                "path",
                "ndc",
                "rgba8",
                "subpath",
                "width",
                "cap",
                "join",
            ),
            builder=_path_subpaths_width_join_ndc,
        ),
        VisualQACase(
            case_id="image/checker_nearest_ndc",
            title="Nearest asymmetric image in NDC",
            family="image",
            required_features=(
                "image",
                "ndc",
                "rgba8",
                "nearest",
                "extent",
                "orientation",
            ),
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
    sizes = np.full(positions.shape[0], 28.0, dtype=np.float32)
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
        arrays={
            "point_positions": positions,
            "point_colors": colors,
            "point_sizes": sizes,
        },
        notes=("Five colored NDC points with a constant nominal pixel size.",),
    )


def _point_diameter_ramp_ndc() -> VisualQAScene:
    diameters = np.array([8.0, 14.0, 22.0, 32.0, 44.0, 58.0], dtype=np.float32)
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
        arrays={
            "point_positions": positions,
            "point_colors": colors,
            "point_diameters": diameters,
        },
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
        arrays={
            "point_positions": positions,
            "point_colors": colors,
            "point_sizes": sizes,
        },
        notes=(
            "Three strongly overlapping semi-transparent points with fixed pixel diameters.",
        ),
    )


def _marker_shapes_ndc() -> VisualQAScene:
    positions = np.array(
        [
            [-0.72, -0.34],
            [-0.36, 0.30],
            [0.0, 0.08],
            [0.36, -0.22],
            [0.72, 0.42],
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
    sizes = np.full(positions.shape[0], 60.0, dtype=np.float32)
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
        notes=(
            "Five conservative built-in marker shapes at asymmetric Y positions with shared dark pixel-width stroke.",
        ),
    )


def _marker_angle_size_stroke_ndc() -> VisualQAScene:
    positions = np.array(
        [
            [-0.72, -0.36],
            [-0.42, 0.30],
            [-0.12, -0.10],
            [0.20, 0.42],
            [0.50, -0.26],
            [0.76, 0.14],
        ],
        dtype=np.float32,
    )
    sizes = np.array([34.0, 42.0, 50.0, 60.0, 72.0, 84.0], dtype=np.float32)
    angles = np.array(
        [0.0, np.pi / 2.0, np.pi, np.pi * 1.5, np.pi / 4.0, -np.pi / 4.0],
        dtype=np.float32,
    )
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
        notes=(
            "Compass-like triangle rotations at asymmetric Y positions with increasing requested pixel diameters and a visible stroke.",
        ),
    )


def _segment_width_cap_ndc() -> VisualQAScene:
    starts = np.array(
        [
            [-0.76, 0.48],
            [-0.70, 0.16],
            [-0.64, -0.18],
            [-0.58, -0.52],
        ],
        dtype=np.float32,
    )
    ends = np.array(
        [
            [0.58, 0.30],
            [0.64, 0.04],
            [0.70, -0.26],
            [0.76, -0.46],
        ],
        dtype=np.float32,
    )
    widths = np.array([8.0, 16.0, 28.0, 42.0], dtype=np.float32)
    colors = np.array(
        [
            [30, 136, 229, 255],
            [0, 137, 123, 255],
            [251, 140, 0, 255],
            [216, 27, 96, 255],
        ],
        dtype=np.uint8,
    )
    visuals = (
        SegmentVisual(
            id="visual:segment-butt-ndc",
            start_positions=starts + np.array([0.0, 0.20], dtype=np.float32),
            end_positions=ends + np.array([0.0, 0.20], dtype=np.float32),
            colors=colors,
            widths=widths,
            cap=StrokeCap.BUTT,
            coordinate_space=CoordinateSpace.NDC,
        ),
        SegmentVisual(
            id="visual:segment-round-ndc",
            start_positions=starts,
            end_positions=ends,
            colors=colors,
            widths=widths,
            cap=StrokeCap.ROUND,
            coordinate_space=CoordinateSpace.NDC,
        ),
        SegmentVisual(
            id="visual:segment-square-ndc",
            start_positions=starts - np.array([0.0, 0.20], dtype=np.float32),
            end_positions=ends - np.array([0.0, 0.20], dtype=np.float32),
            colors=colors,
            widths=widths,
            cap=StrokeCap.SQUARE,
            coordinate_space=CoordinateSpace.NDC,
        ),
    )
    return VisualQAScene(
        case_id="segment/width_cap_ndc",
        visuals=visuals,
        arrays={
            "segment_start_positions": starts,
            "segment_end_positions": ends,
            "segment_colors": colors,
            "segment_widths": widths,
        },
        notes=(
            "Three clearly separated offset rows of independent segments compare butt, round, and square caps with increasing pixel widths.",
        ),
    )


def _segment_alpha_order_ndc() -> VisualQAScene:
    starts = np.array([[-0.70, -0.44], [-0.70, 0.40], [-0.55, -0.06]], dtype=np.float32)
    ends = np.array([[0.72, 0.36], [0.64, -0.46], [0.72, -0.02]], dtype=np.float32)
    colors = np.array(
        [
            [230, 57, 70, 170],
            [42, 157, 143, 170],
            [38, 70, 83, 170],
        ],
        dtype=np.uint8,
    )
    widths = np.array([70.0, 58.0, 46.0], dtype=np.float32)
    visuals = tuple(
        SegmentVisual(
            id=f"visual:segment-alpha-order-{index}",
            start_positions=starts[index : index + 1],
            end_positions=ends[index : index + 1],
            colors=colors[index : index + 1],
            widths=widths[index : index + 1],
            cap=StrokeCap.ROUND,
            coordinate_space=CoordinateSpace.NDC,
        )
        for index in range(starts.shape[0])
    )
    return VisualQAScene(
        case_id="segment/alpha_order_ndc",
        visuals=visuals,
        arrays={
            "segment_start_positions": starts,
            "segment_end_positions": ends,
            "segment_colors": colors,
            "segment_widths": widths,
        },
        notes=(
            "Three thick semi-transparent round-capped segments overlap in creation order.",
        ),
    )


def _path_subpaths_width_join_ndc() -> VisualQAScene:
    miter = np.array(
        [
            [-0.82, 0.54],
            [-0.48, 0.20],
            [-0.20, 0.48],
            [0.08, 0.12],
            [0.38, 0.42],
        ],
        dtype=np.float32,
    )
    round_join = np.array(
        [
            [-0.78, -0.04],
            [-0.42, -0.36],
            [-0.08, -0.06],
            [0.28, -0.40],
            [0.62, -0.08],
        ],
        dtype=np.float32,
    )
    bevel = np.array(
        [
            [0.20, 0.62],
            [0.48, 0.28],
            [0.74, 0.56],
            [0.86, 0.16],
        ],
        dtype=np.float32,
    )
    positions = np.ascontiguousarray(np.vstack([miter, round_join, bevel]))
    path_lengths = (miter.shape[0], round_join.shape[0], bevel.shape[0])
    colors = np.array(
        [
            [30, 136, 229, 255],
            [216, 27, 96, 255],
            [0, 137, 123, 255],
        ],
        dtype=np.uint8,
    )
    widths = np.array([10.0, 22.0, 34.0], dtype=np.float32)
    visual = PathVisual(
        id="visual:path-subpaths-width-join-ndc",
        positions=positions,
        path_lengths=path_lengths,
        colors=colors,
        widths=widths,
        cap=StrokeCap.ROUND,
        join=StrokeJoin.ROUND,
        coordinate_space=CoordinateSpace.NDC,
    )
    return VisualQAScene(
        case_id="path/subpaths_width_join_ndc",
        visuals=(visual,),
        arrays={
            "path_positions": positions,
            "path_lengths": np.array(path_lengths, dtype=np.uint32),
            "path_colors": colors,
            "path_widths": widths,
        },
        notes=(
            "Three open polyline subpaths exercise ordered vertices, round caps/joins, and increasing pixel widths.",
        ),
    )


def _image_checker_nearest_ndc() -> VisualQAScene:
    image = _orientation_image(8)
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
        arrays={"orientation_rgba": image},
        notes=(
            "Small asymmetric RGBA orientation image with nearest interpolation and explicit NDC extent.",
        ),
    )


def _overlay_point_over_image_ndc() -> VisualQAScene:
    image = _orientation_image(10)
    image_visual = ImageVisual(
        id="visual:overlay-checker-image-ndc",
        image=image,
        extent=(-0.85, 0.85, -0.65, 0.65),
        coordinate_space=CoordinateSpace.NDC,
        interpolation=ImageInterpolation.NEAREST,
        origin=ImageOrigin.UPPER,
    )
    positions = np.array(
        [[-0.60, 0.42], [0.58, 0.40], [-0.58, -0.40], [0.55, -0.42]], dtype=np.float32
    )
    colors = np.array(
        [
            [255, 255, 255, 255],
            [20, 20, 20, 255],
            [255, 255, 255, 255],
            [20, 20, 20, 255],
        ],
        dtype=np.uint8,
    )
    sizes = np.full(positions.shape[0], 36.0, dtype=np.float32)
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
            "orientation_rgba": image,
            "point_positions": positions,
            "point_colors": colors,
            "point_sizes": sizes,
        },
        notes=(
            "Asymmetric orientation image with four high-contrast points anchored over distinct colored quadrants.",
        ),
    )


def _orientation_image(size: int) -> np.ndarray:
    image = np.full(
        (size, size, 4), np.array([245, 245, 245, 255], dtype=np.uint8), dtype=np.uint8
    )
    image[0, :] = np.array([35, 40, 45, 255], dtype=np.uint8)
    image[:, 0] = np.array([35, 40, 45, 255], dtype=np.uint8)
    image[:3, :3] = np.array([230, 57, 70, 255], dtype=np.uint8)
    image[:2, -3:] = np.array([42, 157, 143, 255], dtype=np.uint8)
    image[-3:, :2] = np.array([69, 123, 157, 255], dtype=np.uint8)
    image[-2:, -3:] = np.array([251, 191, 36, 255], dtype=np.uint8)
    image[3:-1, 4] = np.array([35, 40, 45, 255], dtype=np.uint8)
    image[3, 4:-2] = np.array([35, 40, 45, 255], dtype=np.uint8)
    return image
