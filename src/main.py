

from multiprocessing import Queue
import sys
from time import sleep
import pygame
from threading import Thread

from ble.packet import Packet
from camera import start_camera_feed
from ble.hidqueueskeyboard import press_and_release
from ble.bleapi import start_ble_conection
from inputstick.packetqueue import packet_queue
from pygamelib.status import ConnectionStatus
pygame.init()


print("starting capture")

screen = pygame.display.set_mode((876, 519), pygame.RESIZABLE)

status = ConnectionStatus()


def update():
    status.draw(screen)
    pygame.display.update()


queue = Queue()

Thread(target=start_camera_feed, args=[screen, update, queue]).start()


Thread(target=start_ble_conection, args=[packet_queue, status]).start()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            queue.put(1)
            sys.exit(0)
        elif event.type == pygame.VIDEORESIZE:
            print(event.size)
        elif event.type == pygame.KEYDOWN:
            print("keydown", event)
        elif event.type == pygame.KEYUP:
            status.key("<arrow down>")
            print("keydown", event)
            press_and_release(event.scancode,)
    sleep(0.03)
    # cv.imshow('frame', frame)
    # if cv.waitKey(1) == ord('q'):
    #    break

# When everything done, release the capture

# cv.destroyAllWindows()
