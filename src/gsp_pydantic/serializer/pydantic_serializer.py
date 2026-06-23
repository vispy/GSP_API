"""Pydantic serializer for GSP data structures."""

# stdlib imports
from typing import Sequence
import typing

# pip imports
import base64

# local imports
from gsp.core.texture import Texture
from gsp.types.serializer_base import SerializerBase
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.types.visual_base import VisualBase
from gsp.visuals.image import Image
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
    PydanticImage,
    PydanticMarkers,
    PydanticPaths,
    PydanticTexts,
    PydanticTexture,
    PydanticViewport,
    PydanticModelMatrix,
    PydanticCamera,
    PydanticScene,
)
from ..types.pydantic_types import PydanticVisual, PydanticPixels, PydanticPoints, PydanticSegments
from ..types.pydantic_types import PydanticTransBuf, PydanticBuffer, PydanticTransformChain, PydanticColor
from ..types.pydantic_dict import PydanticDict


# =============================================================================
#
# =============================================================================
class PydanticSerializer(SerializerBase):
    """Serializer that converts GSP data structures into Pydantic models."""

    def __init__(self, canvas: Canvas):
        """Initialize the PydanticSerializer with a canvas.

        Args:
            canvas (Canvas): The canvas to be used in the serialization.
        """
        self._canvas = canvas

    def serialize(
        self,
        viewports: Sequence[Viewport],
        visuals: Sequence[VisualBase],
        model_matrices: Sequence[TransBuf],
        cameras: Sequence[Camera],
    ) -> PydanticDict:
        """Serialize the provided GSP data structures into a PydanticDict.

        Args:
            viewports (Sequence[Viewport]): The list of viewports to serialize.
            visuals (Sequence[VisualBase]): The list of visual elements to serialize.
            model_matrices (Sequence[TransBuf]): The list of model transformation matrices to serialize.
            cameras (Sequence[Camera]): The list of cameras to serialize.

        Returns:
            PydanticDict: The serialized data as a PydanticDict.
        """
        # =============================================================================
        #
        # =============================================================================

        pydanticCanvas = PydanticCanvas(
            uuid=self._canvas.get_uuid(),
            width=self._canvas.get_width(),
            height=self._canvas.get_height(),
            dpi=self._canvas.get_dpi(),
            background_color=typing.cast(PydanticColor, tuple(self._canvas.get_background_color())),
        )

        pydanticViewports = [
            PydanticViewport(
                uuid=viewport.get_uuid(),
                x=viewport.get_x(),
                y=viewport.get_y(),
                width=viewport.get_width(),
                height=viewport.get_height(),
                background_color=typing.cast(PydanticColor, tuple(viewport.get_background_color())),
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
            if isinstance(visual, Image):
                pydantic_visual = PydanticVisual(
                    type="image",
                    visual=PydanticImage(
                        uuid=visual.get_uuid(),
                        texture=PydanticSerializer._texture_to_pydantic(visual.get_texture()),
                        position=PydanticSerializer._transbuf_to_pydantic(visual.get_position()),
                        image_extent=visual.get_image_extent(),
                        interpolation=visual.get_interpolation().name,
                    ),
                )
                pydantic_visuals.append(pydantic_visual)
            elif isinstance(visual, Markers):
                pydantic_visual = PydanticVisual(
                    type="markers",
                    visual=PydanticMarkers(
                        uuid=visual.get_uuid(),
                        marker_shape=visual.get_marker_shape().name,
                        positions=PydanticSerializer._transbuf_to_pydantic(visual.get_positions()),
                        sizes=PydanticSerializer._transbuf_to_pydantic(visual.get_sizes()),
                        face_colors=PydanticSerializer._transbuf_to_pydantic(visual.get_face_colors()),
                        edge_colors=PydanticSerializer._transbuf_to_pydantic(visual.get_edge_colors()),
                        edge_widths=PydanticSerializer._transbuf_to_pydantic(visual.get_edge_widths()),
                    ),
                )
                pydantic_visuals.append(pydantic_visual)
            elif isinstance(visual, Paths):
                pydantic_visual = PydanticVisual(
                    type="paths",
                    visual=PydanticPaths(
                        uuid=visual.get_uuid(),
                        positions=PydanticSerializer._transbuf_to_pydantic(visual.get_positions()),
                        path_sizes=PydanticSerializer._transbuf_to_pydantic(visual.get_path_sizes()),
                        colors=PydanticSerializer._transbuf_to_pydantic(visual.get_colors()),
                        line_widths=PydanticSerializer._transbuf_to_pydantic(visual.get_line_widths()),
                        cap_style=visual.get_cap_style().name,
                        join_style=visual.get_join_style().name,
                    ),
                )
                pydantic_visuals.append(pydantic_visual)
            elif isinstance(visual, Pixels):
                pydantic_visual = PydanticVisual(
                    type="pixels",
                    visual=PydanticPixels(
                        uuid=visual.get_uuid(),
                        positions=PydanticSerializer._transbuf_to_pydantic(visual.get_positions()),
                        colors=PydanticSerializer._transbuf_to_pydantic(visual.get_colors()),
                        groups=visual.get_groups(),
                    ),
                )
                pydantic_visuals.append(pydantic_visual)
            elif isinstance(visual, Points):
                pydantic_visual = PydanticVisual(
                    type="points",
                    visual=PydanticPoints(
                        uuid=visual.get_uuid(),
                        positions=PydanticSerializer._transbuf_to_pydantic(visual.get_positions()),
                        sizes=PydanticSerializer._transbuf_to_pydantic(visual.get_sizes()),
                        face_colors=PydanticSerializer._transbuf_to_pydantic(visual.get_face_colors()),
                        edge_colors=PydanticSerializer._transbuf_to_pydantic(visual.get_edge_colors()),
                        edge_widths=PydanticSerializer._transbuf_to_pydantic(visual.get_edge_widths()),
                    ),
                )
                pydantic_visuals.append(pydantic_visual)
            elif isinstance(visual, Segments):
                pydantic_visual = PydanticVisual(
                    type="segments",
                    visual=PydanticSegments(
                        uuid=visual.get_uuid(),
                        positions=PydanticSerializer._transbuf_to_pydantic(visual.get_positions()),
                        line_widths=PydanticSerializer._transbuf_to_pydantic(visual.get_line_widths()),
                        cap_style=visual.get_cap_style().name,
                        colors=PydanticSerializer._transbuf_to_pydantic(visual.get_colors()),
                    ),
                )
                pydantic_visuals.append(pydantic_visual)
            elif isinstance(visual, Texts):
                pydantic_visual = PydanticVisual(
                    type="texts",
                    visual=PydanticTexts(
                        uuid=visual.get_uuid(),
                        positions=PydanticSerializer._transbuf_to_pydantic(visual.get_positions()),
                        texts=visual.get_strings(),
                        colors=PydanticSerializer._transbuf_to_pydantic(visual.get_colors()),
                        font_sizes=PydanticSerializer._transbuf_to_pydantic(visual.get_font_sizes()),
                        textAligns=typing.cast(list[int], visual.get_textAligns()),
                        angles=PydanticSerializer._transbuf_to_pydantic(visual.get_angles()),
                        font_name=visual.get_font_name(),
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
            pydantic_transbuf = PydanticTransBuf(
                type="buffer",
                transBuf=PydanticBuffer(
                    count=transbuf.get_count(),
                    buffer_type=transbuf.get_type().name,
                    data_base64=base64.b64encode(transbuf.to_bytearray()).decode("utf-8"),
                ),
            )
            return pydantic_transbuf
        elif isinstance(transbuf, TransformChain):
            pydantic_transbuf = PydanticTransBuf(
                type="transform_chain",
                transBuf=PydanticTransformChain(
                    transform_chain=transbuf.serialize(),
                ),
            )
            return pydantic_transbuf
        else:
            raise ValueError("Unknown TransBuf type")

    @staticmethod
    def _texture_to_pydantic(texture: Texture) -> PydanticTexture:
        pydantic_texture = PydanticTexture(
            uuid=texture.get_uuid(),
            data=PydanticSerializer._transbuf_to_pydantic(texture.get_data()),
            width=texture.get_width(),
            height=texture.get_height(),
        )
        return pydantic_texture


# =============================================================================
