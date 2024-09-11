class DeviceInfo():

    def __init__(self, data: bytearray):
        if data is not None:
            if len(data) > 5:
                self.firmware_type = data[2]
                self.version_major = data[3]
                self.version_minor = data[4]
                self.version_hardware = data[5]
            if len(data) > 20:
                self.security_status = data[19]
                self.password_protected = (data[20] != 0)

    def get_firmware_version(self):
        return self.version_major*100+self.version_minor
