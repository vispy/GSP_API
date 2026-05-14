"""DirectionalLight: light defined by two model-space positions (light and target)."""

# local imports
from ..constants import Constants
from ..types.color import Color
from ..types.transbuf import TransBuf
from .light import Light


class DirectionalLight(Light):
    """A directional light defined by two model-space positions (light and target)."""

    def __init__(
        self,
        light_position: TransBuf,
        target_position: TransBuf,
        color: Color = Constants.Color.white,
        intensity: float = 1.0,
    ) -> None:
        """Initialize a DirectionalLight.

        Args:
            light_position (TransBuf): Model-space position of the light, vec3 buffer of count 1.
            target_position (TransBuf): Model-space position the light points at, vec3 buffer of count 1.
                Direction is computed as normalize(target_position - light_position).
            color (Color): The light color as an rgba bytearray. Defaults to white.
            intensity (float): A float multiplier applied to the light color. Defaults to 1.0.
        """
        super().__init__(color, intensity)

        self._light_position: TransBuf = light_position
        """Model-space position of the light, vec3 buffer of count 1."""
        self._target_position: TransBuf = target_position
        """Model-space position the light points at, vec3 buffer of count 1."""

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_light_position(self) -> TransBuf:
        """Get the model-space position of the light."""
        return self._light_position

    def set_light_position(self, light_position: TransBuf) -> None:
        """Set the model-space position of the light."""
        self._light_position = light_position

    def get_target_position(self) -> TransBuf:
        """Get the model-space position the light points at."""
        return self._target_position

    def set_target_position(self, target_position: TransBuf) -> None:
        """Set the model-space position the light points at."""
        self._target_position = target_position
