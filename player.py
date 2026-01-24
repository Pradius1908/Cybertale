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
            "dead": pygame.image.load("assets/sprites/player_dead.png").convert_alpha(),
        }

        self.direction = "down"
        self.image = self.sprites[self.direction]
        self.rect = self.image.get_rect(center=pos)

        self.hitbox = pygame.Rect(0, 0, 16, 12)
        self.hitbox.midbottom = self.rect.midbottom

        # ---- HP & STATS ----
        self.max_hp = 120
        self.hp = 120
        self.base_attack = 0  # Start at 0 so total damage = weapon damage initially
        self.base_defense = 0 # Base defense
        
        # ---- LEVEL SYSTEM ----
        self.level = 1
        self.xp = 0
        
        self.weapon = None

        # Level Calculation
        self.next_level_xp = 100
        self.level_increment = 100

    def calculate_level_threshold(self):
        # We want: Lvl 1->100. Lvl 2->300 (100+200). Lvl 3->600 (300+300).
        # But user said "limit increment by 100".
        # Current: 100.
        # Next: Current + (CurrentIncrement + 100).
        pass

    def gain_xp(self, amount):
        self.xp += amount
        print(f"Gained {amount} XP. Total: {self.xp}/{self.next_level_xp}")
        while self.xp >= self.next_level_xp:
            self.level_up()

    def level_up(self):
        self.level += 1
        
        # Difficulty scales: 100, 200, 300... for EACH level.
        self.level_increment += 100 
        self.next_level_xp += self.level_increment
        
        self.max_hp += 20
        self.hp = self.max_hp
        self.base_attack += 2
        self.base_defense += 1
        print(f"Level Up! Level: {self.level}, Max HP: {self.max_hp}, Attack: {self.base_attack}, Defense: {self.base_defense}, Next XP: {self.next_level_xp}")

    def teleport(self, pos):
        self.rect.center = pos
        self.hitbox.midbottom = self.rect.midbottom

    def to_dict(self):
        return {
            "hp": self.hp,
            "max_hp": self.max_hp,
            "xp": self.xp,
            "level": self.level,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "next_level_xp": self.next_level_xp,
            "weapon": self.weapon.to_dict() if self.weapon else None
        }

    def load_data(self, data):
        self.hp = data.get("hp", 100)
        self.max_hp = data.get("max_hp", 100)
        self.xp = data.get("xp", 0)
        self.level = data.get("level", 1)
        self.base_attack = data.get("base_attack", 0)
        self.base_defense = data.get("base_defense", 0)
        self.next_level_xp = data.get("next_level_xp", 100)
        
        wd = data.get("weapon")
        if wd:
            from weapon import Weapon
            self.weapon = Weapon.from_dict(wd)
        else:
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
