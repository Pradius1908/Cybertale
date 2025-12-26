import pygame
import textwrap


class TextBox:
    def __init__(
        self,
        texts,     # LIST of strings
        font,
        width=700,
        height=140,
        padding=16,
        text_color=(255, 255, 255),
        bg_color=(20, 20, 20),
        border_color=(200, 200, 200)
    ):
        self.texts = texts
        self.font = font
        self.width = width
        self.height = height
        self.padding = padding

        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color

        self.page = 0
        self.visible = True

        screen = pygame.display.get_surface()
        sw, sh = screen.get_size()

        self.rect = pygame.Rect(
            (sw - width) // 2,
            sh - height - 30,
            width,
            height
        )

        self.lines = self._wrap_text()

    # ---------- INTERNAL ----------

    def _wrap_text(self):
        max_chars = 60
        return textwrap.wrap(self.texts[self.page], max_chars)

    # ---------- CONTROL ----------

    def next_page(self):
        if self.page < len(self.texts) - 1:
            self.page += 1
            self.lines = self._wrap_text()
        else:
            self.visible = False

    # ---------- DRAW ----------

    def draw(self, screen):
        if not self.visible:
            return

        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)

        y = self.rect.y + self.padding
        for line in self.lines:
            surf = self.font.render(line, True, self.text_color)
            screen.blit(surf, (self.rect.x + self.padding, y))
            y += surf.get_height() + 6

        prompt = self.font.render("Press E", True, (180, 180, 180))
        screen.blit(
            prompt,
            (self.rect.right - prompt.get_width() - 10,
             self.rect.bottom - prompt.get_height() - 8)
        )
