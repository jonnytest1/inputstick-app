from ..modifiers import Modifiers
from .hidereport import HidReport


class KeyboardReport(HidReport):

    NONE = 0
    SIZE = 8

    def __init__(self, modifiers: Modifiers, key: int, key2: int = 0, key3: int = 0, key4: int = 0, key5: int = 0, key6: int = 0) -> None:
        self.data = bytearray(KeyboardReport.SIZE)
        self.modifiers = modifiers
        self.key = key

        self.data[0] = modifiers.bytearray_val()
        self.data[2] = key
        self.data[3] = key2
        self.data[4] = key3
        self.data[5] = key4
        self.data[6] = key5
        self.data[7] = key6

    def get_bytes(self):
        return self.data

    def get_byte_count(self) -> int:
        return KeyboardReport.SIZE
