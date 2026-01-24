import pygame
from pytmx.util_pygame import load_pygame
from enemy import Enemy

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
        self.enemies = []
        self.tag_trigger = None
        self.door = None
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

            elif obj.type == "trojan":
                self.trojan_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                # Load trojan sprite (simple centered drawing later)
                self.trojan_image = pygame.image.load("assets/sprites/horse.png").convert_alpha()
                self.trojan_pos = (obj.x, obj.y)
                # Make solid
                self.walls.append(self.trojan_rect)

            elif obj.type == "door":
                self.door = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            
            elif obj.type == "tag":
                self.tag_trigger = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

            elif obj.type == "enemy":
                properties = obj.properties if hasattr(obj, "properties") else {}
                tier = int(properties.get("tier", 1))
                is_tagged = bool(properties.get("tag", False))

                if tier == 3:
                     enemy_type = "WORM"
                elif tier == 4:
                     enemy_type = "VIRUS"
                elif tier == 2:
                     enemy_type = "VOX"
                else:
                     enemy_type = "COIN_THING"
                
                en = Enemy(
                    (int(obj.x + obj.width // 2), int(obj.y + obj.height // 2)),
                    enemy_type
                )
                en.tag = is_tagged
                self.enemies.append(en)

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
        
        if hasattr(self, "trojan_image"):
            screen.blit(self.trojan_image, camera.apply(pygame.Rect(*self.trojan_pos, 0, 0)))

        for enemy in self.enemies:
            enemy.draw(screen, camera)

    def get_solid_walls(self):
        return self.walls[:]
