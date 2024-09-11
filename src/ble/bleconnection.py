import asyncio
from datetime import datetime, timedelta
from enum import Enum
from typing import Union
from bleak import BleakClient
from bleak.backends.service import BleakGATTService
from bleak.backends.characteristic import BleakGATTCharacteristic

from hidinfo import HidInfo
from deviceinfo import DeviceInfo
from packet import Packet

from packettype import Packet_Type
from crc import Crc
from event import ConcreteSubject, Subject
from binascii import crc32
UUID_NRF_RX = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
UUID_NRF_TX = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UUID_NRF_DESC = "00002902-0000-1000-8000-00805f9b34fb"

CRC_OFFSET = 4


class CON_STATE(Enum):
    CONNECTING = 2
    CONNECTED = 3
    READY = 4


class PacketService():
    FLAG_ENCRYPTED = 0x40

    RX_TIMEOUT = timedelta(milliseconds=3000)
    last_rx_time = datetime.fromtimestamp(0)
    rx_state = 0
    rx_length = 0
    rx_pos = 0
    rx_data: bytearray

    RX_TAG = 0
    RX_LENGTH = 1
    RX_DATA = 2

    crc = Crc()

    m_key: Union[bytearray, None] = None

    hid_info = HidInfo()

    def __init__(self, con_ref: "BLEConnection") -> None:
        self.con_ref = con_ref
        pass

    def to_packet(self, data: bytearray):
        payload = data[2:]
        if data[1] & self.FLAG_ENCRYPTED != 0:
            print("HAVE TO DECRYPT")

        crc_compare = int.from_bytes(payload[0:4])
        self.crc.reset()
        self.crc.update(payload, CRC_OFFSET, len(payload)-CRC_OFFSET)

        val = self.crc.value

        if val == crc_compare:
            return payload[4:]

        print("crc mismatch")
        return None

    def handle_message(self, data: bytearray, type: str):
        if type == "EVT":
            packet = self.to_packet(data)

            if packet is None:
                print("got not mathcing packet")
            else:

                cmd = packet[0]
                resp_code = packet[1]
                param = packet[1]
                try:
                    if cmd != Packet_Type.CMD_HID_STATUS.value:
                        print(f"{cmd} for {Packet_Type(cmd)}")
                except ValueError:
                    print(f"{cmd} for unmatched")

                if cmd == Packet_Type.CMD_RUN_FW.value:
                    print("sending CMD_FW_INFO")
                    self.con_ref.send_packet(
                        Packet(True, Packet_Type.CMD_FW_INFO))
                elif cmd == Packet_Type.CMD_FW_INFO.value:
                    print("got info")
                    self.on_fw_info(data, True, True, Packet(
                        True, Packet_Type.CMD_INIT))

                elif cmd == Packet_Type.CMD_INIT.value:
                    if resp_code == Packet_Type.RESP_OK.value:

                        self.con_ref.init_done = True
                        if self.device_info.get_firmware_version() >= 100:
                            self.con_ref.send_packet(
                                Packet(True, Packet_Type.CMD_SET_UPDATE_INTERVAL, 5))
                        else:
                            self.con_ref.set_Status_interval(100)
                    else:
                        print("failed init")

                elif cmd == Packet_Type.CMD_HID_STATUS.value:
                    if self.m_key is None:
                        self.con_ref.init_done = True
                    if self.con_ref.init_done:
                        if param != self.con_ref.last_status_param:
                            self.con_ref.last_status_param = param
                            if param == 5:
                                self.con_ref.on_ready()
                            else:
                                self.con_ref.not_ready()
                    self.hid_info.update(data)

    def on_fw_info(self, data: bytearray, check_auth, enc, next: Packet):
        self.device_info = DeviceInfo(data)

        if check_auth:
            if self.device_info.password_protected:
                if self.m_key is not None:
                    print("do auth")
                else:
                    raise Exception("no security key")
            else:
                if self.m_key is not None:
                    raise Exception("ERROR_SECURITY_NOT_PROTECTED")
                else:
                    self.con_ref.send_packet(next)
        else:
            self.con_ref.send_packet(next)

    def on_byte_rx(self, bytes: bytearray):
        finished_command = False
        print(f"got rx {list(bytes)}")
        for byte in bytes:
            time = datetime.now()
            if time > self.last_rx_time+self.RX_TIMEOUT and False:
                self.rx_state = self.RX_TAG

            if self.rx_state == self.RX_TAG:
                if byte == Packet_Type.START_TAG.value:
                    self.rx_state = self.RX_LENGTH
                else:
                    print("unexpected bytes")
            elif self.rx_state == self.RX_LENGTH:
                self.rx_length = byte
                self.rx_length &= 0x3F
                self.rx_length *= 16
                self.rx_length += 2
                self.rx_pos = 2
                self.rx_data = bytearray(self.rx_length)
                self.rx_data[0] = Packet_Type.START_TAG.value
                self.rx_data[1] = byte

                self.rx_state = self.RX_DATA
            elif self.rx_state == self.RX_DATA:
                if self.rx_pos < self.rx_length:
                    self.rx_data[self.rx_pos] = byte
                    self.rx_pos += 1
                    # print(f"{self.rx_pos}/{self.rx_length}")

                    if self.rx_pos == self.rx_length:
                        # done
                        self.handle_message(self.rx_data, "EVT")
                        finished_command = True
                        self.rx_state = self.RX_TAG

                else:
                    print("BUFFER OVERRUN")
                    self.rx_state = self.RX_TAG

        self.last_rx_time = datetime.now()
        return finished_command


class BLEConnection:
    tx_buffer: list[bytearray] = []
    can_send = False
    last_rx_time = datetime.fromtimestamp(0)

    connection_status = ConcreteSubject()

    last_status_param = 0
    init_done = False
    encryption = False

    PACKET_SIZE = 16

    crc = Crc()

    header: bytearray
    has_header = False

    status_update_interval = 0
    packet_service: PacketService

    def __init__(self, client: BleakClient, service: BleakGATTService) -> None:
        self.client = client
        self.service = service

        rx = service.get_characteristic(UUID_NRF_RX)
        if rx is None:
            raise Exception("no rx characteristic")
        self.rx = rx

        tx = service.get_characteristic(UUID_NRF_TX)
        if tx is None:
            raise Exception("no tx characteristic")
        self.tx = tx
        print("connecting")
        self.connection_status.update(CON_STATE.CONNECTING)
        self.packet_service = PacketService(self)

    async def init(self):
        if self.rx is not None:

            await self.client.start_notify(self.rx, self.on_rx)
            desc = self.rx.get_descriptor(UUID_NRF_DESC)
            if desc is None:
                print("no desc")
            else:
                notif_dec = bytearray(2)
                notif_dec[0] = 1
                descriptor_written = await self.client.write_gatt_descriptor(desc.handle, notif_dec)
                print("written descriptor")

            self.last_rx_time = datetime.now()
            self.can_send = True
            await self.send_next()
            await self.on_connected()
            print("connected")

    async def on_connected(self):
        self.connection_status.update(CON_STATE.CONNECTED)
        self.last_status_param = 0
        self.init_done = False

        self.send_packet(Packet(True, Packet_Type.CMD_RUN_FW))

        await asyncio.sleep(1000)
        if not self.init_done:
            print("reinit after timeout")
            self.send_packet(Packet(True, Packet_Type.CMD_RUN_FW))

        await asyncio.sleep(1000)
        if not self.init_done:
            print("second init failed")
            return False
        return True

    def set_Status_interval(self, interval: int):
        self.status_update_interval = interval

        self.last_rx_time = datetime.now()

        if True:
            self.status_update_interval = 0

    def send_packet(self, packet: Packet):
        data = packet.get_bytes()
        length = len(data)+CRC_OFFSET
        packets = ((length - 1) >> 4) + 1

        result = bytearray(packets * self.PACKET_SIZE)

        result[4:4+len(data)] = data

        self.crc.reset()
        self.crc.update(result, CRC_OFFSET, len(result) - CRC_OFFSET)

        self.crc.set_in_array(result)

        if (self.encryption):
            raise Exception("not implemented")

        header = bytearray(2)
        header[0] = Packet_Type.START_TAG.value
        header[1] = packets

        if (self.encryption):
            header[1] |= Packet_Type.FLAG_ENCRYPTED.value

        if (packet.response):
            header[1] |= Packet_Type.FLAG_RESPOND.value

        if (self.encryption):
            raise Exception("not implemented hmac")

        self.write(header)
        self.write(result)

    def write_header(self, data: bytearray):
        self.header = data
        self.has_header = True

    def add_data_16(self, data: bytearray):

        if self.tx_buffer is not None:
            tmp: bytearray
            offset = 0
            if (self.has_header):
                self.has_header = False
                tmp = bytearray(18)

                tmp[0:2] = self.header
                offset = 2
            else:
                tmp = bytearray(16)

            tmp[offset:16] = data
            self.tx_buffer.append(tmp)
        else:
            print("!! no txBuffer")

    def write(self, out: bytearray):

        if len(out) == 2:
            self.write_header(out)
        elif len(out) == 20:
            raise Exception("hmc")
        else:
            loops = int(len(out)/16)
            offset = 0

            for i in range(loops):
                tmp = bytearray(16)
                tmp = out[offset:offset+16]
                offset += 16
                self.add_data_16(tmp)

            asyncio.create_task(self.send_next())

    def on_rx(self, c: BleakGATTCharacteristic, data: bytearray):
        finished_rx = self.packet_service.on_byte_rx(data)
        if finished_rx:
            self.last_rx_time = datetime.now()
            asyncio.create_task(self.send_next())

    def get_data(self):
        if len(self.tx_buffer) > 0:
            return self.tx_buffer.pop(0)
        return None

    async def send_next(self):
        time = datetime.now().timestamp()

        if ((self.status_update_interval > 0) and (time > (self.last_rx_time.timestamp() + self.status_update_interval - 45))):
            print("abort for status update")
            return

        # status interval check

        if self.can_send:
            data = self.get_data()
            if data is not None:
                self.can_send = False
                r1 = False
                r2 = False
                print(f"writing data {list(data)}")
                r1 = await self.client.write_gatt_char(self.tx, data, response=False)
                print("writing done")
                self.can_send = True
                self.last_rx_time = datetime.now()
                await self.send_next()

            else:
                # print("no data")
                pass
        else:
            pass
            # print("cant send")

    def on_ready(self):
        self.connection_status.update(CON_STATE.READY)

    def not_ready(self):

        self.connection_status.update(CON_STATE.CONNECTED)
