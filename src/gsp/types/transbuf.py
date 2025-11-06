from .buffer import Buffer
from ..transforms.transform_chain import TransformChain


TransBuf = TransformChain | Buffer
"""Type alias for either a TransformChain or a Buffer."""
