"""Matplotlib renderer for GSP visuals."""

# stdlib imports
import os
import io
from typing import Sequence

# pip imports
import matplotlib

from gsp.visuals.texts import Texts

import matplotlib.pyplot
import matplotlib.axes
import matplotlib.artist
import matplotlib.figure

# local imports
from gsp.core.camera import Camera
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.types.visual_base import VisualBase
from gsp.types.transbuf import TransBuf
from gsp.visuals.image import Image
from gsp.visuals.pixels import Pixels
from gsp.visuals.points import Points
from gsp.visuals.markers import Markers
from gsp.visuals.paths import Paths
from gsp.visuals.segments import Segments
from gsp.types.renderer_base import RendererBase

# trick to disable the toolbar in matplotlib
matplotlib.rcParams["toolbar"] = "none"


class MatplotlibRenderer(RendererBase):
    """Matplotlib-based renderer for GSP visuals.

    This renderer implements the GSP rendering interface using Matplotlib as the backend.
    It creates and manages a Matplotlib figure with multiple axes for different viewports,
    and renders various visual types (pixels, points, paths, markers, segments, texts) into them.
    """

    def __init__(self, canvas: Canvas):
        """Initialize the Matplotlib renderer.

        Args:
            canvas: The canvas defining the rendering surface dimensions and DPI.
        """
        self.canvas = canvas
        # Store mapping of viewport UUIDs to axes
        self._axes: dict[str, matplotlib.axes.Axes] = {}
        # Store mapping of visual UUIDs to matplotlib artists
        self._artists: dict[str, matplotlib.artist.Artist] = {}
        # Store group count per visual UUID
        self._group_count: dict[str, int] = {}

        # Create a figure
        figure_width = canvas.get_width() / canvas.get_dpi()
        figure_height = canvas.get_height() / canvas.get_dpi()
        self._figure: matplotlib.figure.Figure = matplotlib.pyplot.figure(figsize=(figure_width, figure_height), dpi=canvas.get_dpi())
        assert self._figure.canvas.manager is not None, "matplotlib figure canvas manager is None"
        self._figure.canvas.manager.set_window_title("Matplotlib")

    def get_canvas(self) -> Canvas:
        """Get the canvas associated with this renderer.

        Returns:
            The canvas instance.
        """
        return self.canvas

    def close(self) -> None:
        """Close the renderer and release resources.

        Stops the Matplotlib event loop and closes the figure.
        """
        # warnings.warn(f"Closing NetworkRenderer does not release any resources.", UserWarning)
        # stop the event loop if any - thus .show(block=True) will return
        self._figure.canvas.stop_event_loop()
        # close the figure
        matplotlib.pyplot.close(self._figure)
        self._figure = None  # type: ignore

    def show(self) -> None:
        """Display the rendered figure in an interactive window.

        This method shows the Matplotlib figure. It does nothing when running
        in test mode (GSP_TEST environment variable set to "True").
        """
        # handle non-interactive mode for tests
        in_test = os.environ.get("GSP_TEST") == "True"
        if in_test:
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
        """Render the scene to an image.

        Args:
            viewports: Sequence of viewport regions to render into.
            visuals: Sequence of visual elements to render.
            model_matrices: Sequence of model transformation matrices for each visual.
            cameras: Sequence of cameras defining view and projection for each visual.
            return_image: Whether to return the rendered image as bytes.
            image_format: Format for the output image (e.g., "png", "jpg").

        Returns:
            The rendered image as bytes in the specified format, or empty bytes if return_image is False.

        Raises:
            AssertionError: If the sequences don't all have the same length.
        """
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
                viewport.get_x() / self.canvas.get_width(),
                viewport.get_y() / self.canvas.get_height(),
                viewport.get_width() / self.canvas.get_width(),
                viewport.get_height() / self.canvas.get_height(),
            )
            axes: matplotlib.axes.Axes = matplotlib.pyplot.axes(axes_rect)
            # this should be -1 to 1 - from normalized device coordinates - https://en.wikipedia.org/wiki/Graphics_pipeline
            # - https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_model_view_projection
            axes.set_xlim(-1, 1)
            axes.set_ylim(-1, 1)
            # hide the borders
            axes.axis("off")
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
            self._figure.savefig(image_png_buffer, format=image_format, dpi=self.canvas.get_dpi())

            image_png_buffer.seek(0)
            image_png_data = image_png_buffer.getvalue()
            image_png_buffer.close()

        return image_png_data

    def _render_visual(self, viewport: Viewport, visual: VisualBase, model_matrix: TransBuf, camera: Camera):
        """Render a single visual in a given viewport using the specified camera."""
        if isinstance(visual, Image):
            from gsp_matplotlib.renderer.matplotlib_renderer_image import RendererImage

            RendererImage.render(self, viewport, visual, model_matrix, camera)
        elif isinstance(visual, Pixels):
            from gsp_matplotlib.renderer.matplotlib_renderer_pixels import RendererPixels

            RendererPixels.render(self, viewport, visual, model_matrix, camera)
        elif isinstance(visual, Points):
            from gsp_matplotlib.renderer.matplotlib_renderer_points import RendererPoints

            RendererPoints.render(self, viewport, visual, model_matrix, camera)
        elif isinstance(visual, Paths):
            from gsp_matplotlib.renderer.matplotlib_renderer_paths import RendererPaths

            RendererPaths.render(self, viewport, visual, model_matrix, camera)
        elif isinstance(visual, Markers):
            from gsp_matplotlib.renderer.matplotlib_renderer_markers import RendererMarkers

            RendererMarkers.render(self, viewport, visual, model_matrix, camera)
        elif isinstance(visual, Segments):
            from gsp_matplotlib.renderer.matplotlib_renderer_segments import RendererSegments

            RendererSegments.render(self, viewport, visual, model_matrix, camera)

        elif isinstance(visual, Texts):
            from gsp_matplotlib.renderer.matplotlib_renderer_texts import RendererTexts

            RendererTexts.render(self, viewport, visual, model_matrix, camera)
        else:
            raise NotImplementedError(f"Rendering for visual type {type(visual)} is not implemented.")

    # =============================================================================
    #
    # =============================================================================

    def get_mpl_axes_for_viewport(self, viewport: Viewport) -> matplotlib.axes.Axes:
        """Get the Matplotlib axes associated with a viewport.

        Args:
            viewport: The viewport to get axes for.

        Returns:
            The Matplotlib Axes object for the given viewport.
        """
        return self._axes[viewport.get_uuid()]

    def get_mpl_figure(self) -> matplotlib.figure.Figure:
        """Get the underlying Matplotlib figure.

        Returns:
            The Matplotlib Figure object used by this renderer.
        """
        return self._figure
