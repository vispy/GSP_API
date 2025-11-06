from ..transforms.transform_chain import TransformChain as TransformChain
from ..types.buffer import Buffer as Buffer
from ..types.transbuf import TransBuf as TransBuf

class TransBufUtils:
    @staticmethod
    def to_buffer(trans_buf: TransBuf) -> Buffer: ...
