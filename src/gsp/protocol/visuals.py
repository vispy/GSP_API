"""First-slice protocol visual models."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import cast

import numpy as np
import numpy.typing as npt

from .color import (
    ScalarColorDomain,
    ScalarColorEncoding,
    ScalarColorSlot,
    validate_scalar_encoding_shape,
)
from .ids import validate_id
from .transforms import VisualTransformBinding


class CoordinateSpace(str, Enum):
    """Coordinate space for first-slice visual placement."""

    NDC = "ndc"
    DATA = "data"


class ImageInterpolation(str, Enum):
    """Image sampling mode."""

    NEAREST = "nearest"
    LINEAR = "linear"


class ImageOrigin(str, Enum):
    """Array row origin for image display."""

    UPPER = "upper"
    LOWER = "lower"


class ImageColormap(str, Enum):
    """Conservative v1 scalar-image colormap vocabulary."""

    GRAY = "gray"


class MarkerShape(str, Enum):
    """Conservative v1 marker shape vocabulary."""

    DISC = "disc"
    SQUARE = "square"
    TRIANGLE = "triangle"
    DIAMOND = "diamond"
    CROSS = "cross"


class StrokeCap(str, Enum):
    """Conservative v1 screen-stroked segment cap vocabulary."""

    BUTT = "butt"
    ROUND = "round"
    SQUARE = "square"


class StrokeJoin(str, Enum):
    """Conservative v1 screen-stroked path join vocabulary."""

    MITER = "miter"
    ROUND = "round"
    BEVEL = "bevel"


class FontRole(str, Enum):
    """Generic backend-resolved text font role."""

    DEFAULT = "default"
    SANS = "sans"
    SERIF = "serif"
    MONOSPACE = "monospace"


class TextAnchorX(str, Enum):
    """Horizontal text layout-box anchor."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class TextAnchorY(str, Enum):
    """Vertical text layout-box anchor."""

    BASELINE = "baseline"
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


class MeshColorMode(str, Enum):
    """Association between mesh colors and geometry."""

    UNIFORM = "uniform"
    FACE = "face"
    VERTEX = "vertex"


class MeshNormalMode(str, Enum):
    """Association between optional mesh normals and geometry."""

    NONE = "none"
    FACE = "face"
    VERTEX = "vertex"


class MeshNormalGeneration(str, Enum):
    """Explicit deterministic mesh normal generation policies."""

    NONE = "none"
    FACE_FLAT = "face_flat"


class MeshShading(str, Enum):
    """Mesh shading semantics."""

    UNLIT_RGBA = "unlit_rgba"
    FLAT_LAMBERT = "flat_lambert"
    TEXTURE2D_UNLIT = "texture2d_unlit"


class MeshUVMode(str, Enum):
    """Association between mesh UVs and geometry."""

    NONE = "none"
    VERTEX = "vertex"


class TextureFilter(str, Enum):
    """Texture sampling filter owned by a textured mesh field slot."""

    NEAREST = "nearest"
    LINEAR = "linear"


class FaceCulling(str, Enum):
    """Conservative mesh face culling policy."""

    NONE = "none"
    BACK = "back"
    FRONT = "front"


class DepthMode(str, Enum):
    """Conservative mesh depth test/write policy."""

    AUTO = "auto"
    DISABLED = "disabled"
    ENABLED = "enabled"


class OpacityPolicy(str, Enum):
    """Mesh opacity policy."""

    ORDINARY_ALPHA = "ordinary_alpha"


FloatArray = npt.NDArray[np.float32] | npt.NDArray[np.float64]
ColorArray = npt.NDArray[np.uint8] | npt.NDArray[np.float32] | npt.NDArray[np.float64]
ImageArray = npt.NDArray[np.uint8] | npt.NDArray[np.float32] | npt.NDArray[np.float64]
IndexArray = npt.NDArray[np.integer]
MarkerShapeTuple = tuple[MarkerShape, ...]
TextAnchorXTuple = tuple[TextAnchorX, ...]
TextAnchorYTuple = tuple[TextAnchorY, ...]

MESH_MATERIAL_UNLIT_RGBA_CAPABILITY = "meshvisual.material.unlit_rgba.v1"
MESH_MATERIAL_FLAT_LAMBERT_CAPABILITY = "meshvisual.material.flat_lambert.v1"
TEXTURE2D_RGBA8_CAPABILITY = "texture2d.rgba8.v1"
MESH_UV_VERTEX2D_CAPABILITY = "meshvisual.uv.vertex2d.v1"
MESH_MATERIAL_TEXTURE2D_UNLIT_CAPABILITY = "meshvisual.material.texture2d_unlit.v1"
MESH_TEXTURE_FILTER_LINEAR_CAPABILITY = "meshvisual.texture_filter.linear.v1"
GSP_VISPY2_PRODUCER_MESH_TEXTURE2D_UNLIT_CAPABILITY = (
    "gsp_vispy2.producer.mesh.texture2d_unlit.v1"
)
GSP_VISPY2_PRODUCER_MESH_TEXTURE_FILTER_LINEAR_CAPABILITY = (
    "gsp_vispy2.producer.mesh.texture_filter.linear.v1"
)
MESH_NORMALS_FACE3D_CAPABILITY = "meshvisual.normals.face3d.v1"
MESH_NORMAL_GENERATION_FACE_FLAT_CAPABILITY = (
    "meshvisual.normal_generation.face_flat.v1"
)


@dataclass(frozen=True, slots=True)
class PointVisual:
    """Semantic point visual model for the protocol reference slice.

    ``sizes`` are rendered screen-pixel diameters, not backend marker-area units.
    """

    id: str
    positions: FloatArray
    colors: ColorArray | None = None
    sizes: FloatArray | float = 1.0
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC
    color_encoding: ScalarColorEncoding | None = None
    transform: VisualTransformBinding | None = None

    def __post_init__(self) -> None:
        validate_id(self.id)
        _validate_visual_transform(self.transform)
        if self.positions.ndim != 2 or self.positions.shape[1] not in (2, 3):
            raise ValueError("positions must have shape (N, 2) or (N, 3)")
        if self.positions.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
            raise TypeError("positions must be float32 or float64")
        if not np.all(np.isfinite(self.positions)):
            raise ValueError("positions must be finite")
        point_count = self.positions.shape[0]

        if isinstance(self.sizes, np.ndarray):
            if self.sizes.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
                raise TypeError("sizes must be float32 or float64")
            if self.sizes.ndim > 1:
                raise ValueError("sizes must be scalar or shape (N,)")
            if self.sizes.shape[0] != point_count:
                raise ValueError("sizes length must match positions")
            if not np.all(np.isfinite(self.sizes)):
                raise ValueError("sizes must be finite")
            if np.any(self.sizes < 0):
                raise ValueError("sizes must be non-negative")
        else:
            if not np.isfinite(self.sizes):
                raise ValueError("sizes must be finite")
            if self.sizes < 0:
                raise ValueError("sizes must be non-negative")

        _validate_color_or_scalar_encoding(
            self.colors,
            self.color_encoding,
            color_shape=(point_count, 4),
            scalar_shape=(point_count,),
            slot=ScalarColorSlot.COLOR,
            domain=ScalarColorDomain.ITEM,
            field_name="colors",
        )


@dataclass(frozen=True, slots=True)
class MarkerVisual:
    """Semantic shaped marker visual model.

    ``sizes`` are rendered screen-pixel diameters. ``angle`` values are radians.
    """

    id: str
    positions: FloatArray
    shape: MarkerShape | MarkerShapeTuple
    fill_colors: ColorArray | None = None
    sizes: FloatArray | float = 1.0
    angle: FloatArray | float = 0.0
    stroke_color: ColorArray = field(
        default_factory=lambda: np.array([0, 0, 0, 255], dtype=np.uint8)
    )
    stroke_width: float = 0.0
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC
    fill_color_encoding: ScalarColorEncoding | None = None
    transform: VisualTransformBinding | None = None

    def __post_init__(self) -> None:
        validate_id(self.id)
        _validate_visual_transform(self.transform)
        point_count = _validate_positions(self.positions)
        _validate_shapes(self.shape, point_count)
        _validate_sizes(self.sizes, point_count)
        _validate_angles(self.angle, point_count)
        _validate_color_or_scalar_encoding(
            self.fill_colors,
            self.fill_color_encoding,
            color_shape=(point_count, 4),
            scalar_shape=(point_count,),
            slot=ScalarColorSlot.FILL,
            domain=ScalarColorDomain.ITEM,
            field_name="fill_colors",
        )
        _validate_rgba_array(self.stroke_color, shape=(4,), field_name="stroke_color")
        if not np.isfinite(self.stroke_width):
            raise ValueError("stroke_width must be finite")
        if self.stroke_width < 0:
            raise ValueError("stroke_width must be non-negative")

    def shape_values(self) -> MarkerShapeTuple:
        """Return one shape per marker."""
        if isinstance(self.shape, MarkerShape):
            return (self.shape,) * int(self.positions.shape[0])
        return self.shape

    def angle_values(self) -> npt.NDArray[np.float32]:
        """Return one angle in radians per marker."""
        if isinstance(self.angle, np.ndarray):
            return np.ascontiguousarray(
                np.asarray(self.angle, dtype=np.float32).reshape(-1)
            )
        return np.full((self.positions.shape[0],), float(self.angle), dtype=np.float32)


@dataclass(frozen=True, slots=True)
class SegmentVisual:
    """Semantic independent line segment visual model.

    ``widths`` are rendered screen-pixel stroke widths. ``cap`` applies to both ends.
    """

    id: str
    start_positions: FloatArray
    end_positions: FloatArray
    colors: ColorArray
    widths: FloatArray | float
    cap: StrokeCap = StrokeCap.BUTT
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC
    transform: VisualTransformBinding | None = None

    def __post_init__(self) -> None:
        validate_id(self.id)
        _validate_visual_transform(self.transform)
        segment_count = _validate_positions(self.start_positions)
        if _validate_positions(self.end_positions) != segment_count:
            raise ValueError("end_positions length must match start_positions")
        if self.end_positions.shape[1] != self.start_positions.shape[1]:
            raise ValueError("end_positions dimensionality must match start_positions")
        _validate_rgba_array(self.colors, shape=(segment_count, 4), field_name="colors")
        _validate_sizes(self.widths, segment_count, field_name="widths")

    def width_values(self) -> npt.NDArray[np.float32]:
        """Return one pixel stroke width per segment."""
        if isinstance(self.widths, np.ndarray):
            return np.ascontiguousarray(
                np.asarray(self.widths, dtype=np.float32).reshape(-1)
            )
        return np.full(
            (self.start_positions.shape[0],), float(self.widths), dtype=np.float32
        )


@dataclass(frozen=True, slots=True)
class PathVisual:
    """Semantic open polyline/subpath visual model.

    ``path_lengths`` partitions ordered vertices into open subpaths. ``widths`` are
    rendered screen-pixel stroke widths and are scalar or per subpath.
    """

    id: str
    positions: FloatArray
    path_lengths: tuple[int, ...]
    colors: ColorArray
    widths: FloatArray | float
    cap: StrokeCap = StrokeCap.BUTT
    join: StrokeJoin = StrokeJoin.MITER
    miter_limit: float = 4.0
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC
    transform: VisualTransformBinding | None = None

    def __post_init__(self) -> None:
        validate_id(self.id)
        _validate_visual_transform(self.transform)
        point_count = _validate_positions(self.positions)
        if not self.path_lengths:
            raise ValueError("path_lengths must not be empty")
        if any(length < 2 for length in self.path_lengths):
            raise ValueError("path_lengths entries must be at least 2")
        if sum(self.path_lengths) != point_count:
            raise ValueError("path_lengths sum must match positions length")
        path_count = len(self.path_lengths)
        _validate_rgba_array(self.colors, shape=(path_count, 4), field_name="colors")
        _validate_sizes(self.widths, path_count, field_name="widths")
        if not np.isfinite(self.miter_limit):
            raise ValueError("miter_limit must be finite")
        if self.miter_limit < 0:
            raise ValueError("miter_limit must be non-negative")

    def width_values(self) -> npt.NDArray[np.float32]:
        """Return one pixel stroke width per subpath."""
        if isinstance(self.widths, np.ndarray):
            return np.ascontiguousarray(
                np.asarray(self.widths, dtype=np.float32).reshape(-1)
            )
        return np.full((len(self.path_lengths),), float(self.widths), dtype=np.float32)


@dataclass(frozen=True, slots=True)
class MeshVisual:
    """Semantic inline indexed triangular mesh visual model."""

    id: str
    positions: FloatArray
    faces: IndexArray
    coordinate_space: CoordinateSpace
    color: ColorArray | None = None
    color_mode: MeshColorMode | None = None
    face_color_encoding: ScalarColorEncoding | None = None
    normal_mode: MeshNormalMode | None = None
    normals: FloatArray | None = None
    normal_generation: MeshNormalGeneration = MeshNormalGeneration.NONE
    shading: MeshShading = MeshShading.UNLIT_RGBA
    texture2d_id: str | None = None
    uv_mode: MeshUVMode = MeshUVMode.NONE
    uvs: FloatArray | None = None
    face_culling: FaceCulling = FaceCulling.NONE
    depth_test: DepthMode = DepthMode.AUTO
    depth_write: DepthMode = DepthMode.AUTO
    order: float = 0.0
    opacity_policy: OpacityPolicy = OpacityPolicy.ORDINARY_ALPHA
    transform: VisualTransformBinding | None = None
    texture_filter: TextureFilter = TextureFilter.NEAREST

    def __post_init__(self) -> None:
        validate_id(self.id)
        _validate_visual_transform(self.transform)
        vertex_count = _validate_positions(self.positions)
        if vertex_count < 3:
            raise ValueError("positions must contain at least three vertices")
        face_count = _validate_faces(self.faces, vertex_count)
        _validate_mesh_degenerate_faces(self.positions, self.faces)
        if not isinstance(self.coordinate_space, CoordinateSpace):
            raise TypeError("coordinate_space must be a CoordinateSpace")

        if self.face_color_encoding is None:
            if self.color is None:
                raise ValueError(
                    "color is required when face_color_encoding is omitted"
                )
            mode = _resolve_mesh_color_mode(
                self.color, self.color_mode, vertex_count, face_count
            )
            _validate_mesh_color(self.color, mode, vertex_count, face_count)
        else:
            if self.color is not None:
                raise ValueError("color and face_color_encoding are mutually exclusive")
            if self.color_mode is not None:
                raise ValueError("color_mode requires color")
            validate_scalar_encoding_shape(
                self.face_color_encoding,
                slot=ScalarColorSlot.FACE_COLOR,
                shape=(face_count,),
                domain=ScalarColorDomain.FACE,
            )

        if not isinstance(self.normal_generation, MeshNormalGeneration):
            raise TypeError("normal_generation must be a MeshNormalGeneration")
        resolved_normal_mode = _resolve_mesh_normal_mode(
            self.normals,
            self.normal_mode,
            vertex_count,
            face_count,
            self.normal_generation,
        )
        if (
            self.normal_generation is not MeshNormalGeneration.NONE
            and self.normals is not None
        ):
            raise ValueError(
                "normal_source_conflict: normal_generation requires normals to be omitted"
            )
        if (
            self.normal_generation is MeshNormalGeneration.FACE_FLAT
            and self.positions.shape[1] != 3
        ):
            raise ValueError("face_flat normal generation requires 3D positions")
        if self.normals is not None:
            _validate_mesh_normals(
                self.normals, resolved_normal_mode, vertex_count, face_count
            )

        if not isinstance(self.shading, MeshShading):
            raise TypeError("shading must be a MeshShading")
        if self.canonical_shading() is MeshShading.FLAT_LAMBERT:
            _validate_mesh_flat_lambert_intrinsic(
                positions=self.positions,
                coordinate_space=self.coordinate_space,
                normals=self.normals,
                normal_mode=self.normal_mode,
                normal_generation=self.normal_generation,
                resolved_normal_mode=resolved_normal_mode,
            )
        _validate_mesh_texture2d_fields(
            shading=self.canonical_shading(),
            texture2d_id=self.texture2d_id,
            uv_mode=self.uv_mode,
            uvs=self.uvs,
            vertex_count=vertex_count,
            normal_mode=resolved_normal_mode,
            normal_generation=self.normal_generation,
            face_color_encoding_present=self.face_color_encoding is not None,
            texture_filter=self.texture_filter,
        )
        if not isinstance(self.face_culling, FaceCulling):
            raise TypeError("face_culling must be a FaceCulling")
        if not isinstance(self.depth_test, DepthMode):
            raise TypeError("depth_test must be a DepthMode")
        if not isinstance(self.depth_write, DepthMode):
            raise TypeError("depth_write must be a DepthMode")
        if not isinstance(self.opacity_policy, OpacityPolicy):
            raise TypeError("opacity_policy must be an OpacityPolicy")
        if isinstance(self.order, bool) or not np.isfinite(self.order):
            raise ValueError("order must be finite")

    def resolved_color_mode(self) -> MeshColorMode:
        """Return the explicit or inferred color association mode."""
        if self.face_color_encoding is not None:
            return MeshColorMode.FACE
        if self.color is None:
            raise ValueError("color is required to resolve mesh color mode")
        return _resolve_mesh_color_mode(
            self.color, self.color_mode, self.positions.shape[0], self.faces.shape[0]
        )

    def resolved_normal_mode(self) -> MeshNormalMode:
        """Return the explicit or inferred normal association mode."""
        return _resolve_mesh_normal_mode(
            self.normals,
            self.normal_mode,
            self.positions.shape[0],
            self.faces.shape[0],
            self.normal_generation,
        )

    def canonical_shading(self) -> MeshShading:
        """Return the GSP 0.2 shading selector."""
        return self.shading

    def normalized_face_normals(self) -> FloatArray:
        """Return explicit or generated S039 DATA-space face normals."""
        if self.canonical_shading() is not MeshShading.FLAT_LAMBERT:
            raise ValueError("normalized_face_normals requires flat_lambert shading")
        if self.normals is not None:
            return _normalize_mesh_normal_array(self.normals, "face normals")
        return _generate_flat_face_normals(self.positions, self.faces)


@dataclass(frozen=True, slots=True)
class ImageVisual:
    """Semantic image visual model for the protocol reference slice."""

    id: str
    image: ImageArray
    extent: tuple[float, float, float, float]
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC
    interpolation: ImageInterpolation = ImageInterpolation.NEAREST
    origin: ImageOrigin = ImageOrigin.UPPER
    colormap: ImageColormap | None = None
    clim: tuple[float, float] | None = None
    color_scale_id: str | None = None

    def __post_init__(self) -> None:
        validate_id(self.id)
        if self.image.ndim not in (2, 3):
            raise ValueError("image must have shape (H, W), (H, W, 3), or (H, W, 4)")
        if self.image.ndim == 3 and self.image.shape[2] not in (3, 4):
            raise ValueError("image channel dimension must be 3 or 4")
        if self.image.shape[0] <= 0 or self.image.shape[1] <= 0:
            raise ValueError("image dimensions must be positive")
        if len(self.extent) != 4 or not all(
            np.isfinite(value) for value in self.extent
        ):
            raise ValueError("extent must contain four finite values")
        if self.extent[0] == self.extent[1] or self.extent[2] == self.extent[3]:
            raise ValueError("extent width and height must be non-zero")
        if self.image.ndim != 2 and (
            self.colormap is not None
            or self.clim is not None
            or self.color_scale_id is not None
        ):
            raise ValueError(
                "colormap, clim, and color_scale_id apply to scalar images only"
            )
        if self.color_scale_id is not None:
            validate_id(self.color_scale_id)
        if self.clim is not None:
            vmin, vmax = self.clim
            if not np.isfinite(vmin) or not np.isfinite(vmax):
                raise ValueError("clim values must be finite")
            if vmin >= vmax:
                raise ValueError("clim minimum must be less than maximum")
        if self.image.dtype == np.dtype(np.uint8):
            return
        if self.image.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
            raise TypeError("image must be uint8, float32, or float64")
        if not np.all(np.isfinite(self.image)):
            raise ValueError("floating point image values must be finite")
        if self.image.ndim == 3 and np.any((self.image < 0.0) | (self.image > 1.0)):
            raise ValueError("floating point RGB/RGBA image values must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class TextVisual:
    """Semantic user-authored text label visual model.

    ``font_size_px`` values are logical screen pixels. ``rotation_rad`` values are
    display-plane radians around the resolved anchor.
    """

    id: str
    texts: Sequence[str]
    positions: FloatArray
    coordinate_space: CoordinateSpace
    rgba: ColorArray = field(
        default_factory=lambda: np.array([0, 0, 0, 255], dtype=np.uint8)
    )
    font_size_px: FloatArray | float = 13.0
    font_role: FontRole = FontRole.DEFAULT
    anchor_x: TextAnchorX | TextAnchorXTuple = TextAnchorX.LEFT
    anchor_y: TextAnchorY | TextAnchorYTuple = TextAnchorY.BASELINE
    rotation_rad: FloatArray | float = 0.0
    z_order: int = 0
    transform: VisualTransformBinding | None = None

    def __post_init__(self) -> None:
        validate_id(self.id)
        _validate_visual_transform(self.transform)
        text_count = _validate_texts(self.texts)
        if _validate_positions(self.positions) != text_count:
            raise ValueError("positions length must match texts")
        if not isinstance(self.coordinate_space, CoordinateSpace):
            raise TypeError("coordinate_space must be a CoordinateSpace")
        _validate_rgba_values(self.rgba, text_count, field_name="rgba")
        _validate_positive_values(
            self.font_size_px, text_count, field_name="font_size_px"
        )
        if not isinstance(self.font_role, FontRole):
            raise TypeError("font_role must be a FontRole")
        _validate_enum_values(
            self.anchor_x, TextAnchorX, text_count, field_name="anchor_x"
        )
        _validate_enum_values(
            self.anchor_y, TextAnchorY, text_count, field_name="anchor_y"
        )
        _validate_angles(self.rotation_rad, text_count, field_name="rotation_rad")
        if isinstance(self.z_order, bool) or not isinstance(self.z_order, int):
            raise TypeError("z_order must be an integer")

    def rgba_values(self) -> ColorArray:
        """Return one RGBA value per text item."""
        if self.rgba.shape == (4,):
            return cast(
                ColorArray,
                np.ascontiguousarray(
                    np.repeat(self.rgba[np.newaxis, :], len(self.texts), axis=0)
                ),
            )
        return cast(ColorArray, np.ascontiguousarray(self.rgba))

    def font_size_values(self) -> npt.NDArray[np.float32]:
        """Return one font size in logical pixels per text item."""
        if isinstance(self.font_size_px, np.ndarray):
            return np.ascontiguousarray(
                np.asarray(self.font_size_px, dtype=np.float32).reshape(-1)
            )
        return np.full((len(self.texts),), float(self.font_size_px), dtype=np.float32)

    def anchor_x_values(self) -> TextAnchorXTuple:
        """Return one horizontal anchor per text item."""
        if isinstance(self.anchor_x, TextAnchorX):
            return (self.anchor_x,) * len(self.texts)
        return self.anchor_x

    def anchor_y_values(self) -> TextAnchorYTuple:
        """Return one vertical anchor per text item."""
        if isinstance(self.anchor_y, TextAnchorY):
            return (self.anchor_y,) * len(self.texts)
        return self.anchor_y

    def rotation_values(self) -> npt.NDArray[np.float32]:
        """Return one rotation in radians per text item."""
        if isinstance(self.rotation_rad, np.ndarray):
            return np.ascontiguousarray(
                np.asarray(self.rotation_rad, dtype=np.float32).reshape(-1)
            )
        return np.full((len(self.texts),), float(self.rotation_rad), dtype=np.float32)


def _validate_positions(positions: FloatArray) -> int:
    if positions.ndim != 2 or positions.shape[1] not in (2, 3):
        raise ValueError("positions must have shape (N, 2) or (N, 3)")
    if positions.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
        raise TypeError("positions must be float32 or float64")
    if not np.all(np.isfinite(positions)):
        raise ValueError("positions must be finite")
    return int(positions.shape[0])


def _validate_visual_transform(transform: VisualTransformBinding | None) -> None:
    if transform is not None and not isinstance(transform, VisualTransformBinding):
        raise TypeError("transform must be a VisualTransformBinding")


def _validate_faces(faces: IndexArray, vertex_count: int) -> int:
    if faces.ndim != 2 or faces.shape[1] != 3:
        raise ValueError("faces must have shape (M, 3)")
    if faces.shape[0] < 1:
        raise ValueError("faces must contain at least one triangle")
    if not np.issubdtype(faces.dtype, np.integer):
        raise TypeError("faces must have integer dtype")
    if np.any(faces < 0) or np.any(faces >= vertex_count):
        raise ValueError("faces indices must reference positions")
    return int(faces.shape[0])


def _validate_mesh_degenerate_faces(positions: FloatArray, faces: IndexArray) -> None:
    triangles = positions[faces]
    if positions.shape[1] == 2:
        edges_a = triangles[:, 1, :] - triangles[:, 0, :]
        edges_b = triangles[:, 2, :] - triangles[:, 0, :]
        area2 = edges_a[:, 0] * edges_b[:, 1] - edges_a[:, 1] * edges_b[:, 0]
        if np.any(area2 == 0):
            raise ValueError("faces must not contain degenerate triangles")
        return
    edges_a = triangles[:, 1, :] - triangles[:, 0, :]
    edges_b = triangles[:, 2, :] - triangles[:, 0, :]
    area2 = np.linalg.norm(np.cross(edges_a, edges_b), axis=1)
    if np.any(area2 == 0):
        raise ValueError("faces must not contain degenerate triangles")


def _resolve_mesh_color_mode(
    color: ColorArray,
    color_mode: MeshColorMode | None,
    vertex_count: int,
    face_count: int,
) -> MeshColorMode:
    if color_mode is not None and not isinstance(color_mode, MeshColorMode):
        raise TypeError("color_mode must be a MeshColorMode")
    if color_mode is not None:
        return color_mode
    if color.shape == (4,):
        return MeshColorMode.UNIFORM
    if color.shape == (face_count, 4) and color.shape != (vertex_count, 4):
        return MeshColorMode.FACE
    if color.shape == (vertex_count, 4) and color.shape != (face_count, 4):
        return MeshColorMode.VERTEX
    if color.shape == (face_count, 4) and color.shape == (vertex_count, 4):
        raise ValueError("color_mode is ambiguous and must be explicit")
    raise ValueError("color shape must match a mesh color mode")


def _validate_mesh_color(
    color: ColorArray, mode: MeshColorMode, vertex_count: int, face_count: int
) -> None:
    if mode is MeshColorMode.UNIFORM:
        _validate_rgba_array(color, shape=(4,), field_name="color")
    elif mode is MeshColorMode.FACE:
        _validate_rgba_array(color, shape=(face_count, 4), field_name="color")
    elif mode is MeshColorMode.VERTEX:
        _validate_rgba_array(color, shape=(vertex_count, 4), field_name="color")
    else:
        raise TypeError("color_mode must be a MeshColorMode")


def _resolve_mesh_normal_mode(
    normals: FloatArray | None,
    normal_mode: MeshNormalMode | None,
    vertex_count: int,
    face_count: int,
    normal_generation: MeshNormalGeneration = MeshNormalGeneration.NONE,
) -> MeshNormalMode:
    if normal_mode is not None and not isinstance(normal_mode, MeshNormalMode):
        raise TypeError("normal_mode must be a MeshNormalMode")
    if not isinstance(normal_generation, MeshNormalGeneration):
        raise TypeError("normal_generation must be a MeshNormalGeneration")
    if normals is None:
        if normal_generation is MeshNormalGeneration.FACE_FLAT:
            if normal_mode in (None, MeshNormalMode.FACE):
                return MeshNormalMode.FACE
            raise ValueError("normal_mode must be face for face_flat normal generation")
        if normal_mode not in (None, MeshNormalMode.NONE):
            raise ValueError("normal_mode requires normals")
        return MeshNormalMode.NONE
    if normal_mode is not None:
        if normal_mode is MeshNormalMode.NONE:
            raise ValueError("normal_mode none requires normals to be omitted")
        return normal_mode
    if normals.shape == (face_count, 3) and normals.shape != (vertex_count, 3):
        return MeshNormalMode.FACE
    if normals.shape == (vertex_count, 3) and normals.shape != (face_count, 3):
        return MeshNormalMode.VERTEX
    if normals.shape == (face_count, 3) and normals.shape == (vertex_count, 3):
        raise ValueError("normal_mode is ambiguous and must be explicit")
    raise ValueError("normals shape must match a mesh normal mode")


def _validate_mesh_normals(
    normals: FloatArray, mode: MeshNormalMode, vertex_count: int, face_count: int
) -> None:
    if normals.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
        raise TypeError("normals must be float32 or float64")
    if mode is MeshNormalMode.FACE:
        expected_shape = (face_count, 3)
    elif mode is MeshNormalMode.VERTEX:
        expected_shape = (vertex_count, 3)
    else:
        raise ValueError("normal_mode none requires normals to be omitted")
    if normals.shape != expected_shape:
        raise ValueError(f"normals must have shape {expected_shape}")
    if not np.all(np.isfinite(normals)):
        raise ValueError("normals must be finite")
    if np.any(np.linalg.norm(normals, axis=1) == 0):
        raise ValueError("normals must be nonzero")


def _validate_mesh_flat_lambert_intrinsic(
    *,
    positions: FloatArray,
    coordinate_space: CoordinateSpace,
    normals: FloatArray | None,
    normal_mode: MeshNormalMode | None,
    normal_generation: MeshNormalGeneration,
    resolved_normal_mode: MeshNormalMode,
) -> None:
    if positions.shape[1] != 3 or coordinate_space is not CoordinateSpace.DATA:
        raise ValueError(
            "flat_lambert_requires_data3d_positions: flat_lambert requires "
            "MeshVisual.positions with shape (N,3) in CoordinateSpace.DATA"
        )
    if normal_mode is not MeshNormalMode.FACE:
        raise ValueError(
            "flat_lambert_requires_face_normals: flat_lambert requires "
            'normal_mode="face"'
        )
    if resolved_normal_mode is not MeshNormalMode.FACE:
        raise ValueError("flat_lambert_requires_face_normals")
    if normals is None:
        if normal_generation is not MeshNormalGeneration.FACE_FLAT:
            raise ValueError(
                "flat_lambert_requires_face_normals: flat_lambert requires "
                "face normals or deterministic face_flat normal generation"
            )
        return
    if normal_generation is not MeshNormalGeneration.NONE:
        raise ValueError(
            "normal_source_conflict: specify either explicit face normals or "
            "face_flat normal generation, not both"
        )


def _validate_mesh_texture2d_fields(
    *,
    shading: MeshShading,
    texture2d_id: str | None,
    uv_mode: MeshUVMode,
    uvs: FloatArray | None,
    vertex_count: int,
    normal_mode: MeshNormalMode,
    normal_generation: MeshNormalGeneration,
    face_color_encoding_present: bool,
    texture_filter: TextureFilter,
) -> None:
    if not isinstance(uv_mode, MeshUVMode):
        raise TypeError("uv_mode must be a MeshUVMode")
    if not isinstance(texture_filter, TextureFilter):
        raise TypeError("texture_filter must be a TextureFilter")
    if shading is not MeshShading.TEXTURE2D_UNLIT:
        if texture_filter is not TextureFilter.NEAREST:
            raise ValueError(
                "meshvisual_texture_filter_inapplicable: linear filtering requires "
                'shading="texture2d_unlit"'
            )
        if texture2d_id is not None:
            validate_id(texture2d_id)
            raise ValueError(
                "meshvisual_texture_lighting_conflict: texture2d_id requires "
                'shading="texture2d_unlit"'
            )
        if uv_mode is not MeshUVMode.NONE or uvs is not None:
            raise ValueError(
                "meshvisual_uv_topology_unsupported: UV fields require "
                'shading="texture2d_unlit"'
            )
        return

    if texture2d_id is None:
        raise ValueError("meshvisual_texture_required: texture2d_id is required")
    validate_id(texture2d_id)
    if uv_mode is not MeshUVMode.VERTEX or uvs is None:
        raise ValueError(
            'meshvisual_uv_required: texture2d_unlit requires uv_mode="vertex" and uvs'
        )
    if (
        normal_mode is not MeshNormalMode.NONE
        or normal_generation is not MeshNormalGeneration.NONE
    ):
        raise ValueError(
            "meshvisual_texture_lighting_conflict: texture2d_unlit does not accept "
            "normal or lighting material fields"
        )
    if face_color_encoding_present:
        raise ValueError(
            "meshvisual_texture_lighting_conflict: texture2d_unlit requires explicit "
            "MeshVisual.color base color"
        )
    _validate_mesh_uvs(uvs, vertex_count)


def _validate_mesh_uvs(uvs: FloatArray, vertex_count: int) -> None:
    if uvs.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
        raise TypeError("meshvisual_uv_shape_mismatch: uvs must be float32 or float64")
    if uvs.shape != (vertex_count, 2):
        raise ValueError(
            f"meshvisual_uv_shape_mismatch: uvs must have shape ({vertex_count}, 2)"
        )
    if not np.all(np.isfinite(uvs)):
        raise ValueError("meshvisual_uv_nonfinite: uvs must be finite")


def _normalize_mesh_normal_array(normals: FloatArray, field_name: str) -> FloatArray:
    lengths = np.linalg.norm(normals, axis=1)
    if not np.all(np.isfinite(lengths)):
        raise ValueError(f"{field_name} lengths must be finite")
    if np.any(lengths == 0.0):
        raise ValueError(f"{field_name} must be nonzero")
    normalized = normals / lengths[:, np.newaxis]
    return cast(FloatArray, np.ascontiguousarray(normalized, dtype=normals.dtype))


def _generate_flat_face_normals(positions: FloatArray, faces: IndexArray) -> FloatArray:
    if positions.shape[1] != 3:
        raise ValueError("face_flat normal generation requires 3D positions")
    triangles = positions[faces]
    edge_a = triangles[:, 1, :] - triangles[:, 0, :]
    edge_b = triangles[:, 2, :] - triangles[:, 0, :]
    raw = np.cross(edge_a, edge_b)
    if not np.all(np.isfinite(raw)):
        raise ValueError(
            "face_normal_generation_degenerate: generated normals must be finite"
        )
    lengths = np.linalg.norm(raw, axis=1)
    if not np.all(np.isfinite(lengths)) or np.any(lengths == 0.0):
        raise ValueError(
            "face_normal_generation_degenerate: cannot generate a face normal "
            "for a degenerate or non-finite triangle"
        )
    normalized = raw / lengths[:, np.newaxis]
    return cast(FloatArray, np.ascontiguousarray(normalized, dtype=positions.dtype))


def validate_mesh_visual_flat_lambert(
    visual: MeshVisual, *, view3d: object | None
) -> None:
    """Validate one mesh/view pair against the accepted S039 Lambert boundary."""
    from .view3d import View3D

    if not isinstance(visual, MeshVisual):
        raise TypeError("visual must be a MeshVisual")
    if visual.canonical_shading() is not MeshShading.FLAT_LAMBERT:
        raise ValueError(
            "validate_mesh_visual_flat_lambert requires flat_lambert shading"
        )
    if not isinstance(view3d, View3D):
        raise ValueError("flat_lambert_requires_view3d: flat_lambert requires a View3D")
    visual.normalized_face_normals()


def validate_mesh_visual_texture2d_unlit(
    visual: MeshVisual, *, texture_resources: Mapping[str, object]
) -> None:
    """Validate one mesh against the accepted S050 Texture2D boundary."""
    from .resources import Texture2D

    if not isinstance(visual, MeshVisual):
        raise TypeError("visual must be a MeshVisual")
    if visual.canonical_shading() is not MeshShading.TEXTURE2D_UNLIT:
        raise ValueError(
            "validate_mesh_visual_texture2d_unlit requires texture2d_unlit shading"
        )
    if visual.texture2d_id is None:
        raise ValueError("meshvisual_texture_required: texture2d_id is required")
    texture = texture_resources.get(visual.texture2d_id)
    if texture is None:
        raise ValueError(
            f"texture2d_unknown_id: unknown Texture2D id {visual.texture2d_id!r}"
        )
    if not isinstance(texture, Texture2D):
        raise TypeError("texture2d_invalid_resource: expected Texture2D")


def _validate_shapes(shape: MarkerShape | MarkerShapeTuple, count: int) -> None:
    if isinstance(shape, MarkerShape):
        return
    if not shape:
        raise ValueError("shape tuple must not be empty")
    if len(shape) != count:
        raise ValueError("shape length must match positions")
    if any(not isinstance(value, MarkerShape) for value in shape):
        raise TypeError("shape entries must be MarkerShape values")


def _validate_sizes(
    sizes: FloatArray | float, count: int, *, field_name: str = "sizes"
) -> None:
    if isinstance(sizes, np.ndarray):
        if sizes.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
            raise TypeError(f"{field_name} must be float32 or float64")
        if sizes.ndim != 1:
            raise ValueError(f"{field_name} must be scalar or shape (N,)")
        if sizes.shape[0] != count:
            raise ValueError(f"{field_name} length must match positions")
        if not np.all(np.isfinite(sizes)):
            raise ValueError(f"{field_name} must be finite")
        if np.any(sizes < 0):
            raise ValueError(f"{field_name} must be non-negative")
        return
    if not np.isfinite(sizes):
        raise ValueError(f"{field_name} must be finite")
    if sizes < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _validate_angles(
    angle: FloatArray | float, count: int, *, field_name: str = "angle"
) -> None:
    if isinstance(angle, np.ndarray):
        if angle.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
            raise TypeError(f"{field_name} must be float32 or float64")
        if angle.ndim != 1:
            raise ValueError(f"{field_name} must be scalar or shape (N,)")
        if angle.shape[0] != count:
            raise ValueError(f"{field_name} length must match positions")
        if not np.all(np.isfinite(angle)):
            raise ValueError(f"{field_name} must be finite")
        return
    if not np.isfinite(angle):
        raise ValueError(f"{field_name} must be finite")


def _validate_texts(texts: Sequence[str]) -> int:
    if isinstance(texts, str) or not isinstance(texts, Sequence):
        raise TypeError("texts must be a sequence of strings")
    for text in texts:
        if not isinstance(text, str):
            raise TypeError("texts entries must be strings")
        try:
            text.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError("texts entries must be UTF-8 serializable") from exc
        for char in text:
            if char == "\n":
                continue
            if ord(char) < 32 or ord(char) == 127:
                raise ValueError("texts entries must not contain control characters")
    return len(texts)


def _validate_positive_values(
    values: FloatArray | float, count: int, *, field_name: str
) -> None:
    _validate_sizes(values, count, field_name=field_name)
    if isinstance(values, np.ndarray):
        if np.any(values <= 0):
            raise ValueError(f"{field_name} must be positive")
        return
    if values <= 0:
        raise ValueError(f"{field_name} must be positive")


def _validate_rgba_values(colors: ColorArray, count: int, *, field_name: str) -> None:
    if colors.shape == (4,):
        _validate_rgba_array(colors, shape=(4,), field_name=field_name)
        return
    _validate_rgba_array(colors, shape=(count, 4), field_name=field_name)


def _validate_color_or_scalar_encoding(
    colors: ColorArray | None,
    encoding: ScalarColorEncoding | None,
    *,
    color_shape: tuple[int, ...],
    scalar_shape: tuple[int, ...],
    slot: ScalarColorSlot,
    domain: ScalarColorDomain,
    field_name: str,
) -> None:
    if encoding is None:
        if colors is None:
            raise ValueError(
                f"{field_name} is required when scalar encoding is omitted"
            )
        if (
            field_name == "colors"
            and len(color_shape) == 2
            and colors.ndim == 2
            and colors.shape[1] == color_shape[1]
            and colors.shape[0] != color_shape[0]
        ):
            raise ValueError("colors length must match positions")
        _validate_rgba_array(colors, shape=color_shape, field_name=field_name)
        return
    if colors is not None:
        raise ValueError(f"{field_name} and scalar encoding are mutually exclusive")
    validate_scalar_encoding_shape(
        encoding, slot=slot, shape=scalar_shape, domain=domain
    )


def _validate_enum_values(
    values: object, enum_type: type[Enum], count: int, *, field_name: str
) -> None:
    if isinstance(values, enum_type):
        return
    if not isinstance(values, tuple):
        raise TypeError(f"{field_name} must be a {enum_type.__name__} or tuple")
    if len(values) != count:
        raise ValueError(f"{field_name} length must match texts")
    if any(not isinstance(value, enum_type) for value in values):
        raise TypeError(f"{field_name} entries must be {enum_type.__name__} values")


def _validate_rgba_array(
    colors: ColorArray, *, shape: tuple[int, ...], field_name: str
) -> None:
    if colors.shape != shape:
        raise ValueError(f"{field_name} must have shape {shape}")
    if colors.dtype == np.dtype(np.uint8):
        return
    if colors.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
        raise TypeError(f"{field_name} must be rgba8, float32, or float64")
    if not np.all(np.isfinite(colors)):
        raise ValueError(f"floating point {field_name} must be finite")
    if np.any((colors < 0.0) | (colors > 1.0)):
        raise ValueError(f"floating point {field_name} must be in [0, 1]")
