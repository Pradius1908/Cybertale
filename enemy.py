import pygame

ENEMY_TYPES = {
    "honey_tier1": {
        "sprite": "assets/sprites/honey.png",
        "max_hp": 40,
        "damage": 10,
        "xp_reward": 50,
        "lore": "Seems to be the remnants of the old honey phishing scam. An extension that stole money from many influencers, companies and people, merely through the use of internet cookies.",
        "dialogue": "T̵r̵u̴s̸t̸ ̷h̵o̷n̴e̸y̶ ̵w̸i̷t̸h̶ ̷y̷o̶u̵r̶ ̶m̴o̷n̵e̸y̴!̴!̸1̴1̶0̸1̸"
    },
    "honey_tier2": {
        "sprite": "assets/sprites/vox.png",
        "max_hp": 80,
        "damage": 20,
        "xp_reward": 100,
        "lore": "A chatbot gone haywire. Possibly made with lecherous intent.",
        "dialogue": "TRUST ME WITH YOUR E̸̗͛N̶͉̋T̸̙̑E̸̗̚Ȓ̸̮Ṫ̴̠A̷̜͒Í̸͓N̸̝̅M̵̢͂Ȅ̵̫N̸͚̈́T̸̞͌!̵͎̇0̷̞̾1̶̘̏0̵̣͘1̸͎̑"
    }
}

class Enemy:
    def __init__(self, pos, enemy_type="honey_tier1"):
        data = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["honey_tier1"])

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

        self.trigger_rect = pygame.Rect(
            self.rect.x + 8,
            self.rect.y + 8,
            self.rect.width - 16,
            self.rect.height - 16
        )

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))
