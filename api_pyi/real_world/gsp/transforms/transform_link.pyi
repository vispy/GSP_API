import abc
from ..types import Buffer as Buffer, BufferType as BufferType
from abc import ABC, abstractmethod

class TransformLink(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def apply(self, buffer_src: Buffer | None) -> Buffer: ...
