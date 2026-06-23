"""Utility functions for working with TransBuf objects.

This module provides helper functions to convert TransBuf instances
to Buffer objects, handling both direct Buffer instances and TransformChain objects.
"""

# stdlib imports
import numpy as np

# local imports
from ..types.transbuf import TransBuf
from ..transforms.transform_chain import TransformChain
from ..types.buffer import Buffer


class TransBufUtils:
    """Utility class for TransBuf conversions and operations.
    
    This class provides static methods for converting TransBuf objects
    to Buffer objects, supporting both direct Buffer instances and
    TransformChain objects that need to be executed.
    """

    @staticmethod
    def to_buffer(trans_buf: TransBuf) -> Buffer:
        """Convert a TransBuf to a Buffer.

        Args:
            trans_buf: A TransBuf object which can be either a Buffer or a TransformChain.

        Returns:
            A Buffer object. If the input is already a Buffer, it's returned directly.
            If it's a TransformChain, it's executed and the resulting Buffer is returned.

        Raises:
            ValueError: If the trans_buf is neither a Buffer nor a TransformChain.
        """
        if isinstance(trans_buf, Buffer):
            return trans_buf
        elif isinstance(trans_buf, TransformChain):
            return trans_buf.run()
        else:
            raise ValueError(f"Unsupported type for transbuf_to_buffer {type(trans_buf)}")
