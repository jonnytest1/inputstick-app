
class HidInfo():

    state: int

    num_lock: bool
    caps_lock: bool
    scroll_lock: bool
    keyboard_report_protocol: bool
    keyboard_ready: bool
    mouse_report_protocol: bool
    mouse_ready: bool
    consumer_ready: bool
    raw_hid_ready: bool
    sent_to_host_info: bool
    keyreport_sent_to_host: int
    mousereport_sent_to_host: int
    consumerreport_sent_to_host: int
    rawhid_report_sent_to_host: int

    def update(self, data: bytearray):
        self.state = data[1]
        leds = data[2]
        if ((leds & 0x01) != 0):
            self.numLock = True
        else:
            self.numLock = False

        self.caps_lock = (leds & 0x02) != 0
        self.scroll_lock = (leds & 0x04) != 0
        self.keyboard_report_protocol = (data[3] == 1)

        self.keyboard_ready = (data[4] != 0)
        self.mouse_report_protocol = (data[5] == 1)
        self.mouse_ready = (data[6] != 0)
        self.consumer_ready = (data[7] != 0)
        if len(data) >= 12:
            if data[11] == 0xFF:
                self.sent_to_host_info = True
                self.keyreport_sent_to_host = data[8] & 0xFF
                self.mousereport_sent_to_host = data[9] & 0xFF
                self.consumerreport_sent_to_host = data[10] & 0xFF
        if len(data) >= 14:
            self.raw_hid_ready = (data[12] != 0)

            self.rawhid_report_sent_to_host = data[13] & 0xFF
        else:
            self.raw_hid_ready = True

        print(self)
