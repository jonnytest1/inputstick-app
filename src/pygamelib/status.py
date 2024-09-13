from typing import Callable
from pygame import Surface
import pygame
pygame.font.init()

fonts = pygame.sysfont.get_fonts()
emoji_fonts = [font for font in fonts if "emoji" in font]

if len(emoji_fonts) == 0:
    raise Exception("no emoji font found")

my_font = pygame.font.SysFont(emoji_fonts[0], 30)


class ConnectionStatus:

    text: str

    def __init__(self):
        self.text = "🛜⏳"
        self.keyV = ""

    def connected(self):
        self.text = "🛜🔗"

    def ready(self):
        self.text = "🛜🚀"

    def key(self, key: str):
        self.keyV = key

    def draw(self, screen: Surface):
        text_surface = my_font.render(
            self.text+" "+self.keyV, False, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
