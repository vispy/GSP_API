"""Type definitions for transformation and buffer combinations.

This module defines type aliases that allow flexible use of either
transformation chains or buffers in the GSP API.
"""

from .buffer import Buffer
from ..transforms.transform_chain import TransformChain


TransBuf = TransformChain | Buffer
"""Type alias for either a TransformChain or a Buffer.

This union type allows functions and methods to accept either a
TransformChain object or a Buffer object, providing flexibility in
how transformations and data buffers are handled throughout the API.
"""
