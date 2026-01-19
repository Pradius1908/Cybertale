import pygame
from choice_textbox import ChoiceTextBox

class CombatScreen:
    def __init__(self, player, enemy, font):
        self.player = player
        self.enemy = enemy
        self.font = font

        self.finished = False
        self.victory = False

        self.message = None

        self.choice_box = ChoiceTextBox(
            ["Choose your action:"],
            ["Attack", "Defend"],
            font
        )

        self.player_image = pygame.image.load(
            "assets/sprites/player_right.png"
        ).convert_alpha()

        self.enemy_image = enemy.image

    def handle_event(self, event):
        if self.message:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if self.message.next_page():
                    self.message = None
                    if self.enemy.hp <= 0:
                        self.finished = True
                        self.victory = True
                    elif self.player_dead():
                        self.finished = True
                        self.victory = False
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.choice_box.move_selection("left")
            elif event.key == pygame.K_d:
                self.choice_box.move_selection("right")
            elif event.key == pygame.K_e:
                if self.choice_box.next_page():
                    self.resolve_turn(self.choice_box.confirm())
                    self.choice_box.reset()

    def resolve_turn(self, action):
        log = []

        if action == "Attack":
            dmg = self.get_player_damage()
            self.enemy.hp -= dmg
            log.append(f"You dealt {dmg} damage.")

        if self.enemy.hp > 0:
            enemy_dmg = self.enemy.damage
            if action == "Defend":
                enemy_dmg //= 2
                log.append("You brace for impact.")

            log.append(f"Enemy dealt {enemy_dmg} damage.")

        self.message = ChoiceTextBox(log, ["OK"], self.font)

    def get_player_damage(self):
        if self.player.weapon:
            return self.player.weapon.damage
        return 4

    def player_dead(self):
        return False  # placeholder for later HP system

    def draw(self, screen):
        screen.fill((10, 10, 10))

        w, h = screen.get_size()

        screen.blit(self.player_image, (100, h // 2 - 50))
        screen.blit(self.enemy_image, (w - 200, h // 2 - 50))

        hp_text = self.font.render(
            f"Enemy HP: {self.enemy.hp}",
            True,
            (255, 80, 80)
        )
        screen.blit(hp_text, (w // 2 - 80, 50))

        if self.message:
            self.message.draw(screen)
        else:
            self.choice_box.draw(screen)
