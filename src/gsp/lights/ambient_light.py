# local imports
from ..constants import Constants
from .light import Light
from ..types.color import Color


class AmbientLight(Light):
    """An omnidirectional ambient light. No position; contributes uniformly to every face."""

    def __init__(self, color: Color = Constants.Color.white, intensity: float = 1.0) -> None:
        """Initialize an AmbientLight.

        Args:
            color (Constants.Color): The light color as an rgba bytearray. Defaults to white.
            intensity (float): A float multiplier applied to the light color. Defaults to 1.0.
        """
        super().__init__()

        self._color: Color = color
        """Light color as an rgba bytearray of 4 uint8 values."""
        self._intensity: float = intensity
        """Intensity multiplier applied to the light color."""

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_color(self) -> Color:
        """Get the light color."""
        return self._color

    def set_color(self, color: Color) -> None:
        """Set the light color."""
        self._color = color

    def get_intensity(self) -> float:
        """Get the light intensity."""
        return self._intensity

    def set_intensity(self, intensity: float) -> None:
        """Set the light intensity."""
        self._intensity = intensity
