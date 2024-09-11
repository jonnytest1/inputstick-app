from typing import Union
from packettype import Packet_Type


class Packet():
    MAX_SUBPACKETS = 17
    MAX_TOTAL_LENGTH = MAX_SUBPACKETS * 16

    def __init__(self, respond: bool, cmd: Packet_Type, param: Union[int, None] = None, data: Union[bytearray, None] = None) -> None:
        self.response = respond
        self.data = bytearray(self.MAX_TOTAL_LENGTH)
        self.data[0] = cmd.value
        self.position = 1

        if param is not None:
            self.data[1] = param
            self.position = 2

        if data is not None:
            pass

    def get_bytes(self):
        return self.data[0:self.position]
