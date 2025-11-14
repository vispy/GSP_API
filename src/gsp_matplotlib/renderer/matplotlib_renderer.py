# stdlib imports
import os
import io
from typing import Sequence

# pip imports
import matplotlib

# trick to disable the toolbar in matplotlib
matplotlib.rcParams["toolbar"] = "none"
import matplotlib.pyplot
import matplotlib.axes
import matplotlib.artist

# local imports
from gsp.core.camera import Camera
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.core.visual_base import VisualBase
from gsp.types.transbuf import TransBuf
from gsp.visuals.pixels import Pixels
from gsp.visuals.points import Points
from gsp.visuals.markers import Markers
from gsp.visuals.paths import Paths
from gsp.visuals.segments import Segments


class MatplotlibRenderer:

    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        # Store mapping of viewport UUIDs to axes
        self._axes: dict[str, matplotlib.axes.Axes] = {}
        # Store mapping of visual UUIDs to matplotlib artists
        self._artists: dict[str, matplotlib.artist.Artist] = {}
        # Store group count per visual UUID
        self._group_count: dict[str, int] = {}

        # Create a figure of 512x512 pixels
        self._figure = matplotlib.pyplot.figure(figsize=(canvas.get_width() / canvas.get_dpi(), canvas.get_height() / canvas.get_dpi()), dpi=canvas.get_dpi())
        assert self._figure.canvas.manager is not None, f"matplotlib figure canvas manager is None"
        self._figure.canvas.manager.set_window_title("Matplotlib")

    def show(self) -> None:
        # handle non-interactive mode for tests
        inTest = os.environ.get("GSP_INTERACTIVE_MODE") == "False"
        if inTest:
            return

        matplotlib.pyplot.show()

    def render(
        self,
        viewports: Sequence[Viewport],
        visuals: Sequence[VisualBase],
        model_matrices: Sequence[TransBuf],
        cameras: Sequence[Camera],
        return_image: bool = True,
        image_format: str = "png",
    ) -> bytes:

        # =============================================================================
        # Sanity checks
        # =============================================================================

        assert (
            len(viewports) == len(visuals) == len(model_matrices) == len(cameras)
        ), f"All length MUST be equal. Mismatched lengths: {len(viewports)} viewports, {len(visuals)} visuals, {len(model_matrices)} model matrices, {len(cameras)} cameras"

        # =============================================================================
        # Create all the axes if needed
        # =============================================================================
        for viewport in viewports:
            if viewport.get_uuid() in self._axes:
                continue
            axes_rect = (
                viewport.get_origin_x() / self.canvas.get_width(),
                viewport.get_origin_y() / self.canvas.get_height(),
                viewport.get_width() / self.canvas.get_width(),
                viewport.get_height() / self.canvas.get_height(),
            )
            axes: matplotlib.axes.Axes = matplotlib.pyplot.axes(axes_rect)
            # this should be -1 to 1 - from normalized device coordinates - https://en.wikipedia.org/wiki/Graphics_pipeline
            # - https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_model_view_projection
            axes.set_xlim(-1, 1)
            axes.set_ylim(-1, 1)
            # store axes for this viewport
            self._axes[viewport.get_uuid()] = axes

        # =============================================================================
        # Render each visual
        # =============================================================================

        for viewport, visual, model_matrix, camera in zip(viewports, visuals, model_matrices, cameras):
            self._render_visual(viewport, visual, model_matrix, camera)

        # =============================================================================
        # Render the output image
        # =============================================================================
        image_png_data = b""

        # honor return_image option
        if return_image:
            # Render the image to a PNG buffer
            image_png_buffer = io.BytesIO()
            matplotlib.pyplot.savefig(image_png_buffer, format=image_format)
            image_png_buffer.seek(0)
            image_png_data = image_png_buffer.getvalue()
            image_png_buffer.close()

        return image_png_data

    def _render_visual(self, viewport: Viewport, visual: VisualBase, model_matrix: TransBuf, camera: Camera):
        """Render a single visual in a given viewport using the specified camera."""

        axes = self._axes[viewport.get_uuid()]
        if isinstance(visual, Pixels):
            from gsp_matplotlib.renderer.matplotlib_renderer_pixels import RendererPixels

            RendererPixels.render(self, axes, visual, model_matrix, camera)
        elif isinstance(visual, Points):
            from gsp_matplotlib.renderer.matplotlib_renderer_points import RendererPoints

            RendererPoints.render(self, axes, visual, model_matrix, camera)
        elif isinstance(visual, Paths):
            from gsp_matplotlib.renderer.matplotlib_renderer_paths import RendererPaths

            RendererPaths.render(self, axes, visual, model_matrix, camera)
        elif isinstance(visual, Markers):
            from gsp_matplotlib.renderer.matplotlib_renderer_markers import RendererMarkers

            RendererMarkers.render(self, axes, visual, model_matrix, camera)
        elif isinstance(visual, Segments):
            from gsp_matplotlib.renderer.matplotlib_renderer_segments import RendererSegments

            RendererSegments.render(self, axes, visual, model_matrix, camera)
        else:
            raise NotImplementedError(f"Rendering for visual type {type(visual)} is not implemented.")

    def get_axes_for_viewport(self, viewport: Viewport) -> matplotlib.axes.Axes:
        return self._axes[viewport.get_uuid()]
