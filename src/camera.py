
from multiprocessing import Queue
from time import sleep
from typing import Callable
from pygame import Surface
import pygame
from pyusbcameraindex import enumerate_usb_video_devices_windows, directshow

from screeninfo import get_monitors

import numpy as np
import cv2 as cv
devs: list[directshow.USBCameraDevice] = enumerate_usb_video_devices_windows()


device = None


for dev in devs:
    if "capture" in dev.name:
        print("using "+dev.name)
        device = dev


screens = get_monitors()


def start_camera_feed(screen: Surface, updater: Callable, exit_queue: Queue):
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, screens[0].width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, screens[0].height)

    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    while exit_queue.qsize() == 0:
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        # Our operations on the frame come here
            # gray = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
        # Display the resulting frame
        cam_surface = pygame.surfarray.make_surface(
            np.transpose(frame, (1, 0, 2)))

        resized_surface = pygame.transform.scale(
            cam_surface, (screen.get_width(), screen.get_height()))

        screen.blit(resized_surface, (0, 0))
        updater()
        sleep(0.033)
    cap.release()
