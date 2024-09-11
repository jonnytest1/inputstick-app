from binascii import crc32

from crc import Crc


crc = Crc()

ar = bytearray(16)
ar[4] = 4


crc.update(ar, 4, 12)


print(crc.value)


crc.set_in_array(ar)

print(ar)
