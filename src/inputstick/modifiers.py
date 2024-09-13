class Modifiers:

    modifier: int

    def __init__(self, modifier: int) -> None:
        self.modifier = modifier

    def bytearray_val(self):
        return self.modifier


modifiers_instance = Modifiers(0)
zero_modifiers = Modifiers(0)
