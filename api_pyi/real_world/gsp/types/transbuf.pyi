from ..transforms.transform_chain import TransformChain as TransformChain
from .buffer import Buffer as Buffer

TransBuf = TransformChain | Buffer
