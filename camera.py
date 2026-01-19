import pygame

class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)

    def apply(self, rect):
        return rect.move(-self.rect.x, -self.rect.y)

    def update(self, target_rect, level_w, level_h):
        x = target_rect.centerx - self.rect.width // 2
        y = target_rect.centery - self.rect.height // 2

        x = max(0, min(x, level_w - self.rect.width))
        y = max(0, min(y, level_h - self.rect.height))

        self.rect.topleft = (x, y)

    def reset(self):
        self.rect.topleft = (0, 0)
