class Room:
    def __init__(self, room_id, x, y):
        self.room_id = room_id
        self.x = x
        self.y = y
        self.connections = {'n': None, 's': None, 'e': None, 'w': None}

    def connect(self, direction, room):
        opposites = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
        self.connections[direction] = room
        room.connections[opposites[direction]] = self