from abc import ABCMeta, abstractmethod


class HidReport(object, metaclass=ABCMeta):

    @abstractmethod
    def get_bytes(self) -> bytearray:
        pass

    @abstractmethod
    def get_byte_count(self) -> int:
        pass
