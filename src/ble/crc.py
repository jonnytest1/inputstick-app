
from binascii import crc32


class Crc:

    value: int

    def reset(self):
        self.value = 0

    def update(self, data: bytearray, start: int, len: int):
        self.value = crc32(data[start:start+len])

    def set_in_array(self, ar: bytearray):
        val = self.value
        bytes = val.to_bytes(4, signed=False)

        ar[0:4] = bytes
