import pygame

class PasswordTextBox:
    def __init__(self, prompt, font):
        self.prompt = prompt
        self.font = font
        self.text = ""

        screen = pygame.display.get_surface()
        w, h = screen.get_size()
        self.rect = pygame.Rect(w//2 - 300, h - 180, 600, 120)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return self.text

            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 16:
                    self.text += event.unicode
        return None

    def draw(self, screen):
        pygame.draw.rect(screen, (20,20,20), self.rect)
        pygame.draw.rect(screen, (200,200,200), self.rect, 2)

        prompt = self.font.render(self.prompt, True, (255,255,255))
        screen.blit(prompt, (self.rect.x + 10, self.rect.y + 10))

        typed = self.font.render(self.text, True, (255,255,0))
        screen.blit(typed, (self.rect.x + 10, self.rect.y + 50))
