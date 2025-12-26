class Door:
    def __init__(self, rect):
        self.rect = rect
        self.is_open = False

    def open(self):
        self.is_open = True

    def is_solid(self):
        return not self.is_open
