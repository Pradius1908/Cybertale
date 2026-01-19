class Weapon:
    def __init__(self, password):
        self.password = password
        self.strength = self.calculate_strength(password)
        self.damage = self.strength * 5

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
