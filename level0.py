import pygame
from pytmx.util_pygame import load_pygame
from door import Door


class Level0:
    def __init__(self):
        # Load Tiled map
        self.tmx_data = load_pygame("maps/level0.tmx")

        self.tile_w = self.tmx_data.tilewidth
        self.tile_h = self.tmx_data.tileheight

        # Map size in pixels (for camera clamping)
        self.pixel_width = self.tmx_data.width * self.tile_w
        self.pixel_height = self.tmx_data.height * self.tile_h

        self.walls = []
        self.doors = []
        self.spawn_pos = None

        # ---------- LOAD OBJECTS ----------
        for obj in self.tmx_data.objects:
            obj_class = obj.type or getattr(obj, "class_", None)

            if obj_class == "wall":
                self.walls.append(
                    pygame.Rect(
                        int(obj.x),
                        int(obj.y),
                        int(obj.width),
                        int(obj.height)
                    )
                )

            elif obj_class == "door":
                self.doors.append(
                    Door(
                        pygame.Rect(
                            int(obj.x),
                            int(obj.y),
                            int(obj.width),
                            int(obj.height)
                        )
                    )
                )

            elif obj_class == "spawnpoint":
                self.spawn_pos = (
                    int(obj.x + obj.width // 2),
                    int(obj.y + obj.height // 2)
                )

        # Safety fallback
        if self.spawn_pos is None:
            self.spawn_pos = (100, 100)

    # ---------- DRAW TILE MAP ----------
    def draw(self, screen, camera):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, surface in layer.tiles():
                    world_rect = pygame.Rect(
                        x * self.tile_w,
                        y * self.tile_h,
                        self.tile_w,
                        self.tile_h
                    )
                    screen.blit(surface, camera.apply(world_rect))

    # ---------- DEBUG (OPTIONAL) ----------
    def debug_draw(self, screen, camera):
        for wall in self.walls:
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                camera.apply(wall),
                2
            )

    # ---------- COLLISION ----------
    def get_solid_walls(self):
        solids = self.walls[:]
        for door in self.doors:
            if not door.is_open:
                solids.append(door.rect)
        return solids
