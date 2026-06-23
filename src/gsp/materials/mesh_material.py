# pip imports
from abc import abstractmethod

import numpy as np

# local imports
from .material import Material
from ..types.transbuf import TransBuf


class MeshMaterial(Material):
    """A simple material class to hold texture mesh material properties."""

    def __init__(
        self,
    ) -> None:
        """Initialize a MeshMaterial instance."""
        super().__init__()

    # =============================================================================
    #
    # =============================================================================

    @abstractmethod
    def check_attributes(self) -> None:
        """Check the attributes of the material for validity."""

    @abstractmethod
    def check_attributes_buffer(self) -> None:
        """Check the attribute buffers of the material for validity."""
