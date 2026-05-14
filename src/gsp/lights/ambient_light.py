"""AmbientLight: omnidirectional light contributing uniformly to every face."""

# local imports
from ..constants import Constants
from ..types.color import Color
from .light import Light


class AmbientLight(Light):
    """An omnidirectional ambient light. No position; contributes uniformly to every face."""

    def __init__(self, color: Color = Constants.Color.white, intensity: float = 1.0) -> None:
        """Initialize an AmbientLight.

        Args:
            color (Color): The light color as an rgba bytearray. Defaults to white.
            intensity (float): A float multiplier applied to the light color. Defaults to 1.0.
        """
        super().__init__(color, intensity)
