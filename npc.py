import pygame

class NPC:
    def __init__(self, pos):
        self.image = pygame.image.load(
            "assets/sprites/clown.png"
        ).convert_alpha()

        self.rect = self.image.get_rect(center=pos)

        # Solid rectangle so player can't walk through NPC
        self.solid_rect = pygame.Rect(
            self.rect.x + 6,
            self.rect.y + 10,
            self.rect.width - 12,
            self.rect.height - 10
        )

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))
	