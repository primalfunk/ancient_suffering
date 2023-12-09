class Room:
    def __init__(self, room_id, x, y):
        self.room_id = room_id
        self.x = x
        self.y = y
        self.region = None
        self.name = ""
        self.connections = {'n': None, 's': None, 'e': None, 'w': None}
        self.lit = 0
        self.has_treasure = False
        self.decorations = []
        self.enemies = []
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0

    def connect(self, direction, room):
        opposites = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
        self.connections[direction] = room
        room.connections[opposites[direction]] = self