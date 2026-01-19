import pygame
from pytmx.util_pygame import load_pygame

class Level2:
    def __init__(self):
        # We assume the user has created or will create maps/level2.tmx
        # If not, this will crash. But based on the request, we must implement the logic.
        try:
            self.tmx = load_pygame("maps/level2.tmx")
        except FileNotFoundError:
            print("ERROR: maps/level2.tmx not found. Transition will fail.")
            # Fallback to level1 map for stability if needed, or just crash
            # For now, let's just let it crash so the user knows to create the map
            raise

        self.tile_w = self.tmx.tilewidth
        self.tile_h = self.tmx.tileheight

        self.pixel_width = self.tmx.width * self.tile_w
        self.pixel_height = self.tmx.height * self.tile_h

        self.walls = []
        self.spawn_pos = (200, 200)

        for obj in self.tmx.objects:
            if obj.type == "wall":
                self.walls.append(
                    pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                )

            elif obj.type == "spawnpoint":
                self.spawn_pos = (
                    int(obj.x + obj.width // 2),
                    int(obj.y + obj.height // 2)
                )

    def draw(self, screen, camera):
        for layer in self.tmx.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, tile in layer.tiles():
                    rect = pygame.Rect(
                        x * self.tile_w,
                        y * self.tile_h,
                        self.tile_w,
                        self.tile_h
                    )
                    screen.blit(tile, camera.apply(rect))

    def get_solid_walls(self):
        return self.walls[:]
