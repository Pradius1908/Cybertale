import pygame
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

    def update(self, keys):
        if keys[pygame.K_w]:
            self.rect.y -= PLAYER_SPEED
            self.hitbox.y -= PLAYER_SPEED
            self.direction = "up"
        elif keys[pygame.K_s]:
            self.rect.y += PLAYER_SPEED
            self.hitbox.y += PLAYER_SPEED
            self.direction = "down"
        elif keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
            self.hitbox.x -= PLAYER_SPEED
            self.direction = "left"
        elif keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
            self.hitbox.x += PLAYER_SPEED
            self.direction = "right"

        self.image = self.sprites[self.direction]

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))
