import pygame
import textwrap

class ChoiceTextBox:
    def __init__(self, texts, choices, font):
        """
        texts   : list of strings (dialogue pages before choice)
        choices : list of strings (e.g. ["Yes", "No"])
        """
        self.texts = texts
        self.choices = choices
        self.font = font

        self.page = 0
        self.selected = 0
        self.visible = True

        screen = pygame.display.get_surface()
        sw, sh = screen.get_size()

        self.rect = pygame.Rect(
            (sw - 700) // 2,
            sh - 200,
            700,
            180
        )

        self.lines = self._wrap_text()

    # ---------- INTERNAL ----------

    def _wrap_text(self):
        return textwrap.wrap(self.texts[self.page], 60)

    # ---------- INPUT ----------

    def next_page(self):
        if self.page < len(self.texts) - 1:
            self.page += 1
            self.lines = self._wrap_text()
            return False  # still showing text
        return True       # ready to choose

    def move_selection(self, direction):
        if direction == "left":
            self.selected = max(0, self.selected - 1)
        elif direction == "right":
            self.selected = min(len(self.choices) - 1, self.selected + 1)

    def confirm(self):
        self.visible = False
        return self.choices[self.selected]

    # ---------- DRAW ----------

    def draw(self, screen):
        if not self.visible:
            return

        pygame.draw.rect(screen, (20, 20, 20), self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)

        y = self.rect.y + 16
        for line in self.lines:
            surf = self.font.render(line, True, (255, 255, 255))
            screen.blit(surf, (self.rect.x + 16, y))
            y += surf.get_height() + 6

        # Only show choices on last page
        if self.page == len(self.texts) - 1:
            x = self.rect.centerx - 100
            y = self.rect.bottom - 40

            for i, choice in enumerate(self.choices):
                color = (255, 255, 0) if i == self.selected else (180, 180, 180)
                surf = self.font.render(choice, True, color)
                screen.blit(surf, (x, y))
                x += 120
        else:
            prompt = self.font.render("Press E", True, (180, 180, 180))
            screen.blit(
                prompt,
                (self.rect.right - prompt.get_width() - 10,
                 self.rect.bottom - prompt.get_height() - 8)
            )
