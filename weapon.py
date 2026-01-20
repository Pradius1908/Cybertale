class Weapon:
    def __init__(self, password):
        self.password = password
        self.strength = self.calculate_strength(password)
        self.strength = self.calculate_strength(password)
        self.damage_modifier = 1.0
        self.jam_chance = 0.0

    @property
    def damage(self):
        return int(self.strength * 5 * self.damage_modifier)

    def to_dict(self):
        return {
            "password": self.password,
            "damage": self.damage,
            "damage_modifier": self.damage_modifier,
            "jam_chance": self.jam_chance
        }

    @staticmethod
    def from_dict(data):
        w = Weapon(data["password"])
        # damage is calculated property, but we might want to verify integrity or just trust password re-calc
        w.damage_modifier = data.get("damage_modifier", 1.0)
        w.jam_chance = data.get("jam_chance", 0.0)
        return w

    def calculate_strength(self, pwd):
        score = 0

        if len(pwd) >= 8:
            score += 1
        if any(c.isupper() for c in pwd):
            score += 1
        if any(c.islower() for c in pwd):
            score += 1
        if any(c.isdigit() for c in pwd):
            score += 1
        if any(not c.isalnum() for c in pwd):
            score += 1

        return score
