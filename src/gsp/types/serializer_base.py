"""Base class for serializers that convert canvas scenes to various formats."""

# stdlib imports
from abc import ABC, abstractmethod
from typing import Sequence, Any

# local imports
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.types.visual_base import VisualBase
from gsp.core.camera import Camera
from gsp.types.transbuf import TransBuf


class SerializerBase(ABC):
    """Abstract base class for serializing canvas scenes.

    This class defines the interface for serializers that convert a canvas
    with viewports, visuals, model matrices, and cameras into a serialized format.
    """

    @abstractmethod
    def __init__(self, canvas: Canvas):
        """Initialize the serializer with a canvas.

        Args:
            canvas: The canvas to serialize.
        """
        pass

    @abstractmethod
    def serialize(
        self,
        viewports: Sequence[Viewport],
        visuals: Sequence[VisualBase],
        model_matrices: Sequence[TransBuf],
        cameras: Sequence[Camera],
    ) -> dict[str, Any]:
        """Serialize the scene components into a dictionary.

        Args:
            viewports: Sequence of viewport objects to serialize.
            visuals: Sequence of visual objects to serialize.
            model_matrices: Sequence of transformation buffers for model matrices.
            cameras: Sequence of camera objects to serialize.

        Returns:
            A dictionary containing the serialized scene data.
        """
        pass
