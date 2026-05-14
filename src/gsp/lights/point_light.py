# local imports
from ..constants import Constants
from ..types.color import Color
from ..types.transbuf import TransBuf
from .light import Light


class PointLight(Light):
    """A point light source defined by a single model-space position."""

    def __init__(
        self,
        position: TransBuf,
        color: Color = Constants.Color.white,
        intensity: float = 1.0,
    ) -> None:
        """Initialize a PointLight.

        Args:
            position (TransBuf): Model-space position as a vec3 buffer of count 1.
                Transformed to world space via the mesh's model_matrix at render time.
            color (Constants.Color): The light color as an rgba bytearray. Defaults to white.
            intensity (float): A float multiplier applied to the light color. Defaults to 1.0.
        """
        super().__init__()

        self._position: TransBuf = position
        """Model-space position, vec3 buffer of count 1."""
        self._color: Color = color
        """Light color as an rgba bytearray of 4 uint8 values."""
        self._intensity: float = intensity
        """Intensity multiplier applied to the light color."""

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_position(self) -> TransBuf:
        """Get the model-space position of the light."""
        return self._position

    def set_position(self, position: TransBuf) -> None:
        """Set the model-space position of the light."""
        self._position = position

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
