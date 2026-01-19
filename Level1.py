import pygame
from pytmx.util_pygame import load_pygame
from npc import NPC
from enemy import Enemy

class Level1:
    def __init__(self):
        self.tmx = load_pygame("maps/level1.tmx")

        self.tile_w = self.tmx.tilewidth
        self.tile_h = self.tmx.tileheight

        self.pixel_width = self.tmx.width * self.tile_w
        self.pixel_height = self.tmx.height * self.tile_h

        self.walls = []
        self.spawn_pos = (200, 200)

        self.npcs = []
        self.npc_triggers = []

        self.enemies = []

        self.weapon_triggers = []
        self.weapon_triggers = []
        self.weapon_visible = True
        self.exit_rect = None

        for obj in self.tmx.objects:
            if obj.type == "door": # User said "door object at the end"
                self.exit_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

            if obj.type == "wall":
                self.walls.append(
                    pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                )

            elif obj.type == "spawnpoint":
                self.spawn_pos = (
                    int(obj.x + obj.width // 2),
                    int(obj.y + obj.height // 2)
                )

            elif obj.type == "npc":
                self.npcs.append(
                    NPC(
                        (int(obj.x + obj.width // 2),
                         int(obj.y + obj.height // 2))
                    )
                )

            elif obj.type == "npc_trigger":
                self.npc_triggers.append(
                    pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                )

            elif obj.type == "enemy":
                properties = obj.properties if hasattr(obj, "properties") else {}
                tier = int(properties.get("tier", 1))
                
                # Default to tier 1 if unspecified or invalid
                if tier == 2:
                    enemy_type = "honey_tier2"
                else:
                    enemy_type = "honey_tier1"
                
                self.enemies.append(
                    Enemy(
                        (int(obj.x + obj.width // 2),
                         int(obj.y + obj.height // 2)),
                        enemy_type
                    )
                )

            elif obj.type == "weapon_trigger":
                self.weapon_triggers.append(
                    pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                )



    def draw(self, screen, camera):
        for layer in self.tmx.visible_layers:
            if layer.name == "weapon_layer" and not self.weapon_visible:
                continue

            if hasattr(layer, "tiles"):
                for x, y, tile in layer.tiles():
                    rect = pygame.Rect(
                        x * self.tile_w,
                        y * self.tile_h,
                        self.tile_w,
                        self.tile_h
                    )
                    screen.blit(tile, camera.apply(rect))

        for npc in self.npcs:
            npc.draw(screen, camera)

        for enemy in self.enemies:
            enemy.draw(screen, camera)

    def get_solid_walls(self):
        solids = self.walls[:]
        for npc in self.npcs:
            solids.append(npc.solid_rect)
        return solids
