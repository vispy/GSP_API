# stdlib imports
from typing import Sequence, Any
import typing
import base64
import json

# pip imports
import pydantic_core

# local imports
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.types.visual_base import VisualBase
from gsp.visuals.pixels import Pixels
from gsp.visuals.points import Points
from gsp.visuals.segments import Segments
from gsp.visuals.paths import Paths
from gsp.visuals.markers import Markers
from gsp.visuals.segments import Segments
from gsp.types.cap_style import CapStyle
from gsp.types.join_style import JoinStyle
from gsp.visuals.markers import MarkerShape
from gsp.types.transbuf import TransBuf
from gsp.types.buffer import Buffer
from gsp.types.buffer_type import BufferType
from gsp.transforms.transform_chain import TransformChain
from gsp.core.camera import Camera
from ..types.pydantic_types import PydanticCanvas, PydanticViewport, PydanticModelMatrix, PydanticCamera, PydanticScene
from ..types.pydantic_types import PydanticTransBuf, PydanticBuffer, PydanticTransformChain
from ..types.pydantic_types import PydanticVisual, PydanticPixels, PydanticPoints, PydanticSegments, PydanticPaths, PydanticMarkers
from ..types.pydantic_dict import PydanticDict


class PydanticParser:
    def __init__(self):
        pass

    def parse(self, json_dict: PydanticDict) -> tuple[
        Canvas,
        list[Viewport],
        list[VisualBase],
        list[TransBuf],
        list[Camera],
    ]:

        json_str = json.dumps(json_dict, indent=4)
        pydantic_scene = PydanticScene.model_validate(pydantic_core.from_json(json_str, allow_partial=True))

        # =============================================================================
        # Parse Pydantic Canvas
        # =============================================================================
        pydantic_canvas = pydantic_scene.canvas
        canvas = Canvas(pydantic_canvas.width, pydantic_canvas.height, pydantic_canvas.dpi)
        canvas._uuid = pydantic_canvas.uuid

        # =============================================================================
        # Parse Pydantic Viewports
        # =============================================================================
        viewports: list[Viewport] = []  # Placeholder implementation
        for pydantic_viewport in pydantic_scene.viewports:
            viewport = Viewport(
                pydantic_viewport.x,
                pydantic_viewport.y,
                pydantic_viewport.width,
                pydantic_viewport.height,
            )
            viewport._uuid = pydantic_viewport.uuid
            viewports.append(viewport)

        # =============================================================================
        # Parse Pydantic Visuals
        # =============================================================================
        visuals: list[VisualBase] = []  # Placeholder implementation
        for pydantic_visual in pydantic_scene.visuals:
            visual = PydanticParser._pydantic_to_visual(pydantic_visual)
            visuals.append(visual)

        # =============================================================================
        # Parse Pydantic Model Matrices
        # =============================================================================
        model_matrices: list[TransBuf] = []  # Placeholder implementation
        for pydantic_model_matrix in pydantic_scene.model_matrices:
            model_matrix = PydanticParser._pydantic_to_transbuf(pydantic_model_matrix.model_matrix)
            model_matrices.append(model_matrix)

        # =============================================================================
        # Parse Pydanticy Cameras
        # =============================================================================
        cameras: list[Camera] = []
        for pydantic_camera in pydantic_scene.cameras:
            view_matrix = PydanticParser._pydantic_to_transbuf(pydantic_camera.view_matrix)
            projection_matrix = PydanticParser._pydantic_to_transbuf(pydantic_camera.projection_matrix)
            camera = Camera(view_matrix, projection_matrix)
            camera._uuid = pydantic_camera.uuid
            cameras.append(camera)

        # =============================================================================
        # Return the renderer arguments
        # =============================================================================
        return canvas, viewports, visuals, model_matrices, cameras

    @staticmethod
    def _pydantic_to_visual(pydantic_visual: PydanticVisual) -> VisualBase:
        if pydantic_visual.type == "pixels":
            pydantic_pixels = typing.cast(PydanticPixels, pydantic_visual.visual)
            positions = PydanticParser._pydantic_to_transbuf(pydantic_pixels.positions)
            colors = PydanticParser._pydantic_to_transbuf(pydantic_pixels.colors)
            groups = pydantic_pixels.groups
            pixels = Pixels(positions, colors, groups)
            pixels._uuid = pydantic_pixels.uuid
            return pixels
        elif pydantic_visual.type == "points":
            pydantic_points = typing.cast(PydanticPoints, pydantic_visual.visual)
            positions = PydanticParser._pydantic_to_transbuf(pydantic_points.positions)
            sizes = PydanticParser._pydantic_to_transbuf(pydantic_points.sizes)
            face_colors = PydanticParser._pydantic_to_transbuf(pydantic_points.face_colors)
            edge_colors = PydanticParser._pydantic_to_transbuf(pydantic_points.edge_colors)
            edge_widths = PydanticParser._pydantic_to_transbuf(pydantic_points.edge_widths)
            points = Points(positions, sizes, face_colors, edge_colors, edge_widths)
            points._uuid = pydantic_points.uuid
            return points
        elif pydantic_visual.type == "segments":
            pydantic_segments = typing.cast(PydanticSegments, pydantic_visual.visual)
            positions = PydanticParser._pydantic_to_transbuf(pydantic_segments.positions)
            line_widths = PydanticParser._pydantic_to_transbuf(pydantic_segments.line_widths)
            cap_style = CapStyle[pydantic_segments.cap_style]
            colors = PydanticParser._pydantic_to_transbuf(pydantic_segments.colors)
            segments = Segments(positions, line_widths, cap_style, colors)
            segments._uuid = pydantic_segments.uuid
            return segments
        elif pydantic_visual.type == "paths":
            pydantic_paths = typing.cast(PydanticPaths, pydantic_visual.visual)
            positions = PydanticParser._pydantic_to_transbuf(pydantic_paths.positions)
            path_sizes = PydanticParser._pydantic_to_transbuf(pydantic_paths.path_sizes)
            colors = PydanticParser._pydantic_to_transbuf(pydantic_paths.colors)
            line_widths = PydanticParser._pydantic_to_transbuf(pydantic_paths.line_widths)
            cap_style = CapStyle[pydantic_paths.cap_style]
            join_style = JoinStyle[pydantic_paths.join_style]
            paths = Paths(positions, path_sizes, colors, line_widths, cap_style, join_style)
            paths._uuid = pydantic_paths.uuid
            return paths
        elif pydantic_visual.type == "markers":
            pydantic_markers = typing.cast(PydanticMarkers, pydantic_visual.visual)
            marker_shape = MarkerShape[pydantic_markers.marker_shape]
            positions = PydanticParser._pydantic_to_transbuf(pydantic_markers.positions)
            sizes = PydanticParser._pydantic_to_transbuf(pydantic_markers.sizes)
            face_colors = PydanticParser._pydantic_to_transbuf(pydantic_markers.face_colors)
            edge_colors = PydanticParser._pydantic_to_transbuf(pydantic_markers.edge_colors)
            edge_widths = PydanticParser._pydantic_to_transbuf(pydantic_markers.edge_widths)
            markers = Markers(marker_shape, positions, sizes, face_colors, edge_colors, edge_widths)
            markers._uuid = pydantic_markers.uuid
            return markers
        else:
            raise ValueError(f"Unknown PydanticVisual type: {pydantic_visual.type}")

    @staticmethod
    def _pydantic_to_transbuf(pydantic_transbuf: PydanticTransBuf) -> TransBuf:
        if pydantic_transbuf.type == "buffer":
            pydantic_buffer = typing.cast(PydanticBuffer, pydantic_transbuf.transBuf)
            count = pydantic_buffer.count
            buffer_type = BufferType[pydantic_buffer.buffer_type]
            buffer_data = bytearray(base64.b64decode(pydantic_buffer.data_base64))
            buffer = Buffer.from_bytearray(buffer_data, buffer_type)
            assert buffer.get_count() == count, f"Buffer count mismatch: expected {count}, got {buffer.get_count()}"
            return buffer
        elif pydantic_transbuf.type == "transform_chain":
            pydantic_transform_chain = typing.cast(PydanticTransformChain, pydantic_transbuf.transBuf)
            deserialized_transform = TransformChain.deserialize(pydantic_transform_chain.transform_chain)
            buffer = deserialized_transform.run()
            return buffer
        else:
            raise ValueError(f"Unknown PydanticTransBuf type: {pydantic_transbuf.type}")
