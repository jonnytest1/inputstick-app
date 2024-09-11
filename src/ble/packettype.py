from enum import Enum


class Packet_Type(Enum):
    START_TAG = 0x55
    FLAG_RESPOND = 0x80

    FLAG_ENCRYPTED = 0x40
    CMD_RUN_FW = 0x04
    CMD_FW_INFO = 16
    CMD_INIT = 17
    CMD_INIT_AUTH = 18
    CMD_HID_DATA_RAW = 39
    CMD_INIT_AUTH_HMAC = 48
    CMD_SET_UPDATE_INTERVAL = 49
    CMD_HID_STATUS = 47

    RESP_OK = 1
