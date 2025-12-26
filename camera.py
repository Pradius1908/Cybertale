import pygame

class Camera:
    def __init__(self, screen_width, screen_height):
        self.rect = pygame.Rect(0, 0, screen_width, screen_height)

    def update(self, target_rect, map_width, map_height):
        # Center camera on player
        self.rect.center = target_rect.center

        # Clamp camera to map bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.right > map_width:
            self.rect.right = map_width
        if self.rect.bottom > map_height:
            self.rect.bottom = map_height

    def apply(self, rect):
        # Convert world coordinates → screen coordinates
        return rect.move(-self.rect.x, -self.rect.y)
