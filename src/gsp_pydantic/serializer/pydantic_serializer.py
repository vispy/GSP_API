# stdlib imports
from typing import Sequence
import typing

# pip imports
import base64

# local imports
from gsp.types.serializer_base import SerializerBase
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.types.visual_base import VisualBase
from gsp.visuals.markers import Markers
from gsp.visuals.paths import Paths
from gsp.visuals.pixels import Pixels
from gsp.visuals.points import Points
from gsp.visuals.segments import Segments
from gsp.visuals.texts import Texts
from gsp.core.camera import Camera
from gsp.types.transbuf import TransBuf
from gsp.types.buffer import Buffer
from gsp.transforms.transform_chain import TransformChain
from ..types.pydantic_types import (
    PydanticCanvas,
    PydanticMarkers,
    PydanticPaths,
    PydanticTexts,
    PydanticViewport,
    PydanticModelMatrix,
    PydanticCamera,
    PydanticScene,
)
from ..types.pydantic_types import PydanticVisual, PydanticPixels, PydanticPoints, PydanticSegments
from ..types.pydantic_types import PydanticTransBuf, PydanticBuffer, PydanticTransformChain
from ..types.pydantic_dict import PydanticDict


# =============================================================================
#
# =============================================================================
class PydanticSerializer(SerializerBase):

    def __init__(self, canvas: Canvas):
        self._canvas = canvas

    def serialize(
        self,
        viewports: Sequence[Viewport],
        visuals: Sequence[VisualBase],
        model_matrices: Sequence[TransBuf],
        cameras: Sequence[Camera],
    ) -> PydanticDict:

        # =============================================================================
        #
        # =============================================================================

        pydanticCanvas = PydanticCanvas(
            uuid=self._canvas.get_uuid(),
            width=self._canvas.get_width(),
            height=self._canvas.get_height(),
            dpi=self._canvas.get_dpi(),
        )

        pydanticViewports = [
            PydanticViewport(
                uuid=viewport.get_uuid(),
                x=viewport.get_x(),
                y=viewport.get_y(),
                width=viewport.get_width(),
                height=viewport.get_height(),
            )
            for viewport in viewports
        ]

        pydantic_visuals = PydanticSerializer._visuals_to_pydantic(visuals)

        pydantic_model_matrices = [PydanticModelMatrix(model_matrix=PydanticSerializer._transbuf_to_pydantic(model_matrix)) for model_matrix in model_matrices]

        pydantic_cameras = [
            PydanticCamera(
                uuid=camera.get_uuid(),
                view_matrix=PydanticSerializer._transbuf_to_pydantic(camera.get_view_matrix()),
                projection_matrix=PydanticSerializer._transbuf_to_pydantic(camera.get_projection_matrix()),
            )
            for camera in cameras
        ]

        # =============================================================================
        #
        # =============================================================================

        pydantic_scene = PydanticScene(
            canvas=pydanticCanvas,
            viewports=pydanticViewports,
            visuals=pydantic_visuals,
            model_matrices=pydantic_model_matrices,
            cameras=pydantic_cameras,
        )

        pydantic_scene_dict: PydanticDict = pydantic_scene.model_dump()

        return pydantic_scene_dict  # Placeholder for JSON byte output

    # =============================================================================
    # Static methods
    # =============================================================================

    @staticmethod
    def _visuals_to_pydantic(visuals: Sequence[VisualBase]) -> list[PydanticVisual]:
        pydantic_visuals: list[PydanticVisual] = []
        for visual in visuals:
            if isinstance(visual, Markers):
                markers = typing.cast(Markers, visual)
                pydantic_visual = PydanticVisual(
                    type="markers",
                    visual=PydanticMarkers(
                        uuid=markers.get_uuid(),
                        marker_shape=markers.get_marker_shape().name,
                        positions=PydanticSerializer._transbuf_to_pydantic(markers.get_positions()),
                        sizes=PydanticSerializer._transbuf_to_pydantic(markers.get_sizes()),
                        face_colors=PydanticSerializer._transbuf_to_pydantic(markers.get_face_colors()),
                        edge_colors=PydanticSerializer._transbuf_to_pydantic(markers.get_edge_colors()),
                        edge_widths=PydanticSerializer._transbuf_to_pydantic(markers.get_edge_widths()),
                    ),
                )
                pydantic_visuals.append(pydantic_visual)
            elif isinstance(visual, Paths):
                paths = typing.cast(Paths, visual)
                pydantic_visual = PydanticVisual(
                    type="paths",
                    visual=PydanticPaths(
                        uuid=paths.get_uuid(),
                        positions=PydanticSerializer._transbuf_to_pydantic(paths.get_positions()),
                        path_sizes=PydanticSerializer._transbuf_to_pydantic(paths.get_path_sizes()),
                        colors=PydanticSerializer._transbuf_to_pydantic(paths.get_colors()),
                        line_widths=PydanticSerializer._transbuf_to_pydantic(paths.get_line_widths()),
                        cap_style=paths.get_cap_style().name,
                        join_style=paths.get_join_style().name,
                    ),
                )
                pydantic_visuals.append(pydantic_visual)
            elif isinstance(visual, Pixels):
                pixels = typing.cast(Pixels, visual)
                pydantic_visual = PydanticVisual(
                    type="pixels",
                    visual=PydanticPixels(
                        uuid=pixels.get_uuid(),
                        positions=PydanticSerializer._transbuf_to_pydantic(pixels.get_positions()),
                        colors=PydanticSerializer._transbuf_to_pydantic(pixels.get_colors()),
                        groups=pixels.get_groups(),
                    ),
                )
                pydantic_visuals.append(pydantic_visual)
            elif isinstance(visual, Points):
                points = typing.cast(Points, visual)
                pydantic_visual = PydanticVisual(
                    type="points",
                    visual=PydanticPoints(
                        uuid=points.get_uuid(),
                        positions=PydanticSerializer._transbuf_to_pydantic(points.get_positions()),
                        sizes=PydanticSerializer._transbuf_to_pydantic(points.get_sizes()),
                        face_colors=PydanticSerializer._transbuf_to_pydantic(points.get_face_colors()),
                        edge_colors=PydanticSerializer._transbuf_to_pydantic(points.get_edge_colors()),
                        edge_widths=PydanticSerializer._transbuf_to_pydantic(points.get_edge_widths()),
                    ),
                )
                pydantic_visuals.append(pydantic_visual)
            elif isinstance(visual, Segments):
                segments = typing.cast(Segments, visual)
                pydantic_visual = PydanticVisual(
                    type="segments",
                    visual=PydanticSegments(
                        uuid=segments.get_uuid(),
                        positions=PydanticSerializer._transbuf_to_pydantic(segments.get_positions()),
                        line_widths=PydanticSerializer._transbuf_to_pydantic(segments.get_line_widths()),
                        cap_style=segments.get_cap_style().name,
                        colors=PydanticSerializer._transbuf_to_pydantic(segments.get_colors()),
                    ),
                )
                pydantic_visuals.append(pydantic_visual)
            elif isinstance(visual, Texts):
                texts = typing.cast(Texts, visual)
                pydantic_visual = PydanticVisual(
                    type="texts",
                    visual=PydanticTexts(
                        uuid=texts.get_uuid(),
                        positions=PydanticSerializer._transbuf_to_pydantic(texts.get_positions()),
                        texts=texts.get_strings(),
                        colors=PydanticSerializer._transbuf_to_pydantic(texts.get_colors()),
                        font_sizes=PydanticSerializer._transbuf_to_pydantic(texts.get_font_sizes()),
                        anchors=PydanticSerializer._transbuf_to_pydantic(texts.get_anchors()),
                        angles=PydanticSerializer._transbuf_to_pydantic(texts.get_angles()),
                        font_name=texts.get_font_name(),
                    ),
                )
                pydantic_visuals.append(pydantic_visual)
            else:
                raise NotImplementedError(f"Serialization for this Visual type {type(visual)} is not implemented yet")

        # return the list of pydantic visuals
        return pydantic_visuals

    @staticmethod
    def _transbuf_to_pydantic(transbuf: TransBuf) -> PydanticTransBuf:
        if isinstance(transbuf, Buffer):
            buffer = typing.cast(Buffer, transbuf)
            pydantic_transbuf = PydanticTransBuf(
                type="buffer",
                transBuf=PydanticBuffer(
                    count=buffer.get_count(),
                    buffer_type=buffer.get_type().name,
                    data_base64=base64.b64encode(buffer.to_bytearray()).decode("utf-8"),
                ),
            )
            return pydantic_transbuf
        elif isinstance(transbuf, TransformChain):
            transform_chain = typing.cast(TransformChain, transbuf)
            pydantic_transbuf = PydanticTransBuf(
                type="transform_chain",
                transBuf=PydanticTransformChain(
                    transform_chain=transform_chain.serialize(),
                ),
            )
            return pydantic_transbuf
        else:
            raise ValueError("Unknown TransBuf type")
