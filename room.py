import random
import math

class Room:
    def __init__(self, room_id, x, y, map):
        self.map = map
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
        self.atmo = ""
        self.color = ""
        self.is_target = False
    
    def connect(self, direction, room):
        opposites = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
        self.connections[direction] = room
        room.connections[opposites[direction]] = self

    def euclidean_distance(self, room1, room2):
        return math.sqrt((room1.x - room2.x)**2 + (room1.y - room2.y)**2)

    def get_random_distant_room(self):
        distance_func = self.euclidean_distance
        min_distance = self.map.size // 2
        distant_rooms = [room for room in self.map.rooms.values()
                        if distance_func(room, self) >= min_distance]
        if distant_rooms:
            return random.choice(distant_rooms)
        else:
            return None  # No room found with the required distance