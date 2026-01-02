"""class ViewportUnitUtils: Convert between pixel/cm to ndc units in a viewport."""

# local imports
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.utils.unit_utils import UnitUtils


class ViewportUnitUtils:
    """Convert between pixel/cm to ndc units in a viewport."""

    def __init__(self, canvas: Canvas, viewport: Viewport) -> None:
        """Initialize the converter with a canvas and viewport."""
        self._canvas = canvas
        self._viewport = viewport

    def get_canvas(self) -> Canvas:
        """Get the canvas."""
        return self._canvas

    def get_viewport(self) -> Viewport:
        """Get the viewport."""
        return self._viewport

    def _get_canvas_width_px(self) -> int:
        return self._canvas.get_width()

    def _get_canvas_height_px(self) -> int:
        return self._canvas.get_height()

    def _get_canvas_width_cm(self) -> float:
        screen_ppi = self._canvas.get_dpi()
        canvas_width_in = self._canvas.get_width() / screen_ppi
        canvas_width_cm = UnitUtils.in_to_cm(canvas_width_in)
        return canvas_width_cm

    def _get_canvas_height_cm(self) -> float:
        screen_ppi = self._canvas.get_dpi()
        canvas_height_in = self._canvas.get_height() / screen_ppi
        canvas_height_cm = UnitUtils.in_to_cm(canvas_height_in)
        return canvas_height_cm

    def _get_viewport_width_px(self) -> int:
        return self._viewport.get_width()

    def _get_viewport_height_px(self) -> int:
        return self._viewport.get_height()

    def _get_viewport_width_cm(self) -> float:
        canvas_viewport_ratio = self._viewport.get_width() / self._canvas.get_width()
        canvas_width_cm = self._get_canvas_width_cm()
        viewport_width_cm = canvas_viewport_ratio * canvas_width_cm
        return viewport_width_cm

    def _get_viewport_height_cm(self) -> float:
        canvas_viewport_ratio = self._viewport.get_height() / self._canvas.get_height()
        canvas_height_cm = self._get_canvas_height_cm()
        viewport_height_cm = canvas_viewport_ratio * canvas_height_cm
        return viewport_height_cm

    def delta_pixel_to_ndc(self, delta_pixel_x: float, delta_pixel_y: float) -> tuple[float, float]:
        """Convert a delta in pixels to a delta in NDC units."""
        viewport_range_ndc_x = 2.0
        viewport_range_ndc_y = 2.0

        delta_ndc_x = (delta_pixel_x / self._get_viewport_width_px()) * viewport_range_ndc_x
        delta_ndc_y = (delta_pixel_y / self._get_viewport_height_px()) * viewport_range_ndc_y

        return (delta_ndc_x, delta_ndc_y)

    def delta_cm_to_ndc(self, delta_cm_x: float, delta_cm_y: float) -> tuple[float, float]:
        """Convert a delta in cm to a delta in NDC units."""
        viewport_range_ndc_x = 2.0
        viewport_range_ndc_y = 2.0

        delta_ndc_x = (delta_cm_x / self._get_viewport_width_cm()) * viewport_range_ndc_x
        delta_ndc_y = (delta_cm_y / self._get_viewport_height_cm()) * viewport_range_ndc_y

        return (delta_ndc_x, delta_ndc_y)
