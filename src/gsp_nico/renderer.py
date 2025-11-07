# Stdlib imports
from typing import Literal
import typing

# Pip imports
import numpy as np
import matplotlib.pyplot

# Local imports
from .canvas import Canvas
from .viewport import Viewport
from gsp_matplotlib.renderer import MatplotlibRenderer as GspMatplotlibRenderer
from gsp_datoviz.renderer.renderer import DatovizRenderer as GspDatovizRenderer
from gsp.core.camera import Camera as GspCamera
from gsp.core.viewport import Viewport as GspViewport
from gsp.core.visual_base import VisualBase as GspVisualBase
from gsp.types.buffer import Buffer as GspBuffer
from gsp.types.buffer_type import BufferType as GspBufferType
from gsp_matplotlib.extra.bufferx import Bufferx


class Renderer:
    def __init__(self, backend: Literal["matplotlib", "datoviz"]):
        self.backend = backend
        self.gsp_renderer = None

    def render(self, canvas: Canvas, output_format: str) -> bytes:
        if self.gsp_renderer is None:
            if self.backend == "matplotlib":
                self.gsp_renderer = GspMatplotlibRenderer(canvas.gsp_canvas)
            elif self.backend == "datoviz":
                self.gsp_renderer = GspDatovizRenderer(canvas.gsp_canvas)
            else:
                raise ValueError(f"Unsupported backend: {self.backend}")

        # Convert parameters
        gsp_viewports: list[GspViewport] = []
        gsp_visuals: list[GspVisualBase] = []
        gsp_model_matrices: list[GspBuffer] = []
        gsp_cameras: list[GspCamera] = []
        for untyped_viewport in canvas.untyped_viewports:
            viewport = typing.cast(Viewport, untyped_viewport)
            for visual_index, visual in enumerate(viewport.visuals):

                gsp_viewports.append(viewport.gsp_viewport)
                gsp_visuals.append(visual.gsp_pixels)

                gsp_model_matrices.append(visual.gsp_model_matrix)
                gsp_view_matrix = viewport.gsp_view_matrices[visual_index]
                gsp_proj_matrix = viewport.gsp_proj_matrices[visual_index]
                gsp_camera = GspCamera(gsp_view_matrix, gsp_proj_matrix)

                gsp_cameras.append(gsp_camera)

        # Render the image
        rendered_image = self.gsp_renderer.render(
            viewports=gsp_viewports,
            visuals=gsp_visuals,
            model_matrices=gsp_model_matrices,
            cameras=gsp_cameras,
            image_format=output_format,
        )

        matplotlib.pyplot.show()

        return rendered_image
