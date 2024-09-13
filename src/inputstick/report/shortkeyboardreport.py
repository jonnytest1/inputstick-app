from hidereport import HidReport
from modifiers import Modifiers


class ShortKeyboardReport(HidReport):

    def __init__(self, modifier: Modifiers, key: int) -> None:
        super().__init__()

        self.data = bytearray()
        self.data[0] = modifier.bytearray_val()
        self.data[1] = key
