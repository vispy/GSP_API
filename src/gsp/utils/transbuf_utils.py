# stdlib imports
import numpy as np
import typing


# local imports
from ..types.transbuf import TransBuf
from ..transforms.transform_chain import TransformChain
from ..types.buffer import Buffer


class TransBufUtils:
    @staticmethod
    def to_buffer(trans_buf: TransBuf) -> Buffer:
        """Convert a TransBuf to a Buffer."""
        if isinstance(trans_buf, Buffer):
            buffer = typing.cast(Buffer, trans_buf)
            return buffer
        elif isinstance(trans_buf, TransBuf):
            transform_chain = typing.cast(TransformChain, trans_buf)
            buffer = transform_chain.run()
            return buffer
        else:
            raise ValueError(f"Unsupported type for transbuf_to_buffer {type(trans_buf)}")
