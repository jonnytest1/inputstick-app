from queue import Queue

from ble.packet import Packet


packet_queue: Queue[Packet] = Queue()
