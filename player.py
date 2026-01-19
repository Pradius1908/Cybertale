import pygame
from settings import HP, XP
from settings import PLAYER_SPEED

class Player:
    def __init__(self, pos):
        self.sprites = {
            "up": pygame.image.load("assets/sprites/player_up.png").convert_alpha(),
            "down": pygame.image.load("assets/sprites/player_down.png").convert_alpha(),
            "left": pygame.image.load("assets/sprites/player_left.png").convert_alpha(),
            "right": pygame.image.load("assets/sprites/player_right.png").convert_alpha(),
        }

        self.direction = "down"
        self.image = self.sprites[self.direction]
        self.rect = self.image.get_rect(center=pos)

        self.hitbox = pygame.Rect(0, 0, 16, 12)
        self.hitbox.midbottom = self.rect.midbottom

        # ---- HP ----
        self.max_hp = 120
        self.hp = 120
        self.xp = XP

        self.weapon = None

    def update(self, keys):
        moved = False

        if keys[pygame.K_w]:
            self.rect.y -= PLAYER_SPEED
            self.hitbox.y -= PLAYER_SPEED
            self.direction = "up"
            moved = True
        elif keys[pygame.K_s]:
            self.rect.y += PLAYER_SPEED
            self.hitbox.y += PLAYER_SPEED
            self.direction = "down"
            moved = True
        elif keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
            self.hitbox.x -= PLAYER_SPEED
            self.direction = "left"
            moved = True
        elif keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
            self.hitbox.x += PLAYER_SPEED
            self.direction = "right"
            moved = True

        if moved:
            self.image = self.sprites[self.direction]

    def equip_weapon(self, weapon):
        self.weapon = weapon

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))
