import pygame
from pytmx.util_pygame import load_pygame

class Level1:
    def __init__(self):
        # Load a DIFFERENT TMX map
        self.tmx_data = load_pygame("maps/level1.tmx")

        # Everything else is identical to Level0:
        # walls, doors, spawn_pos, etc.
