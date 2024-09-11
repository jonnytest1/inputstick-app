

import sys
import numpy as np
from screeninfo import get_monitors
import cv2 as cv
import pygame
from pyusbcameraindex import enumerate_usb_video_devices_windows, directshow

pygame.init()

devs: list[directshow.USBCameraDevice] = enumerate_usb_video_devices_windows()


device = None


for dev in devs:
    if "capture" in dev.name:
        print("using "+dev.name)
        device = dev


print("starting capture")
cap = cv.VideoCapture(0, cv.CAP_DSHOW)

screen = pygame.display.set_mode((876, 519), pygame.RESIZABLE)


def blitCamFrame(frame, screen):
    screen.blit(frame, (0, 0))
    return screen


screens = get_monitors()

cap.set(cv.CAP_PROP_FRAME_WIDTH, screens[0].width)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, screens[0].height)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    screen.fill([0, 0, 0])
    # Capture frame-by-frame
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
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.VIDEORESIZE:
            print(event.size)
    # cv.imshow('frame', frame)
    # if cv.waitKey(1) == ord('q'):
    #    break
# When everything done, release the capture
cap.release()
# cv.destroyAllWindows()
