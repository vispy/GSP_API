"""Base Light class for GSP API; owns color + intensity for all subclasses."""

# local imports
from ..constants import Constants
from ..types.color import Color


class Light:
    """Base class for scene lights. Carries the shared color + intensity attributes."""

    def __init__(self, color: Color = Constants.Color.white, intensity: float = 1.0) -> None:
        """Initialize a Light.

        Args:
            color (Color): The light color as an rgba bytearray. Defaults to white.
            intensity (float): A float multiplier applied to the light color. Defaults to 1.0.
        """
        self._color: Color = color
        """Light color as an rgba bytearray of 4 uint8 values."""
        self._intensity: float = intensity
        """Intensity multiplier applied to the light color."""

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
