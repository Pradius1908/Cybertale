import pygame

ENEMY_TYPES = {
    "COIN_THING": {
        "sprite": "assets/sprites/honey.png",
        "max_hp": 40,
        "damage": 10,
        "xp_reward": 50,
        "lore": "Seems to be the remnants of the old social engineering scam. An extension that stole money from many influencers, companies and people, merely through the use of internet cookies.",
        "dialogue": "T̵r̵u̴s̸t̸ ̷h̵o̷n̴e̸y̶ ̵w̸i̷t̸h̶ ̷y̷o̶u̵r̶ ̶m̴o̷n̵e̸y̴!̴!̸1̴1̶0̸1̸"
    },
    "VOX": {
        "sprite": "assets/sprites/vox.png",
        "max_hp": 80,
        "damage": 20,
        "xp_reward": 100,
        "lore": "A chatbot gone haywire. Possibly made with lecherous intent.",
        "dialogue": "TRUST ME WITH YOUR E̸̗͛N̶͉̋T̸̙̑E̸̗̚Ȓ̸̮Ṫ̴̠A̷̜͒Í̸͓N̸̝̅M̵̢͂Ȅ̵̫N̸͚̈́T̸̞͌!̵͎̇0̷̞̾1̶̘̏0̵̣͘1̸͎̑"
    },
    "WORM": {
        "sprite": "assets/sprites/worm.png",
        "max_hp": 90,
        "damage": 25,
        "xp_reward": 200,
        "lore": "A self-replicating burrower. Its attacks corrupt your drivers, causing weapon malfunctions.",
        "dialogue": "I... burrow... deep...",
        "backfire_chance": 0.5  # 50% chance to cause backfire on hit
    },
    "VIRUS": {
        "sprite": "assets/sprites/virus.png",
        "max_hp": 120,
        "damage": 30,
        "xp_reward": 500,
        "lore": "A pure malicious payload. Extremely dangerous.",
        "dialogue": "DELETE. DELETE. DELETE."
    }
}

class Enemy:
    def __init__(self, pos, enemy_type="COIN_THING"):
        data = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["COIN_THING"])

        self.type = enemy_type
        self.image = pygame.image.load(data["sprite"]).convert_alpha()
        self.rect = self.image.get_rect(center=pos)

        self.max_hp = data["max_hp"]
        self.hp = self.max_hp
        self.hp = self.max_hp
        self.damage = data["damage"]
        self.xp_reward = data.get("xp_reward", 0)
        self.lore = data.get("lore", "Unknown entity.")
        self.dialogue = data.get("dialogue", "...")
        self.backfire_chance = data.get("backfire_chance", 0.0)
        
        self.tag = False # Default tag status

        self.trigger_rect = pygame.Rect(
            self.rect.x + 8,
            self.rect.y + 8,
            self.rect.width - 16,
            self.rect.height - 16
        )

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))
