

from enum import Enum
from ble.bleconnection import CON_STATE, BLEConnection
from ble.packettype import Packet_Type
from inputstick.hidtransaction import HidTransaction


class KeyCodes(Enum):
    KEY_ARROW_RIGHT = 79
    KEY_ARROW_LEFT = 80
    KEY_ARROW_DOWN = 81
    KEY_ARROW_UP = 82


async def type(con: BLEConnection, lut: list[list[int]], text: str, modifiers, speed=1):
    if con.connection_status.state == CON_STATE.READY:
        for c in text:
            transaction = HidTransaction(Packet_Type.CMD_HID_DATA_KEYB_FAST)
            # con.send_packet()

    else:
        print("not ready")
