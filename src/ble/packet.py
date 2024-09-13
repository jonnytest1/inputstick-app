from typing import Union
from .packettype import Packet_Type


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

        # if data is not None:
        #    pass

    def modify_byte(self, pos: int, byte: int):
        self.data[pos] = byte

    def get_bytes(self):
        return self.data[0:self.position]

    def get_remaining_free_space(self):
        return Packet.MAX_TOTAL_LENGTH - self.position

    def add_bytes(self, data: bytearray):
        if data is None:
            return True

        data_len = len(data)
        if self.get_remaining_free_space() >= data_len:
            # TODO double check
            self.data[self.position:self.position+data_len] = data
            self.position += data_len
            return True
        return False
