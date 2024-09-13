from ble.deviceinfo import DeviceInfo
from ble.hidinfo import HidInfo
from ble.packettype import Packet_Type
from .hidqueueskeyboard import keyboardQueue


class InputStickHID:
    hid_info = HidInfo()

    def on_rx_data(self, data: bytearray):
        cmd = data[0]

        if cmd == Packet_Type.CMD_FW_INFO.value:
            device_info = DeviceInfo(data)
            if (device_info.get_firmware_version() >= 100):
                keyboardQueue.set_capacity(128)
               # mouseQueue.setCapacity(64)
               # consumerQueue.setCapacity(64)

        elif cmd == Packet_Type.CMD_HID_STATUS.value:
            self.hid_info.update(data=data)

            keyboardQueue.update(self.hid_info)
