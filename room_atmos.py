import random

class RoomAtmos:
    def __init__(self, map, data):
        self.map = map
        self.colors = data["adjectives"]["colors"]
        self.atmos = data["atmos"]

    def create_atmosphere(self):
        colors = self.colors.copy()
        atmos = self.atmos.copy()
        print(f"length of colors: {len(colors)}; length of atmos: {len(atmos)}")
        random.shuffle(colors)
        random.shuffle(atmos)
        for room in self.map.rooms.values():
            if len(colors) == 0:
                colors = self.colors.copy()
            else:
                color = colors[0]
                colors.pop(0)
            if len(atmos) == 0:
                atmos = self.atmos.copy()
            else:
                atmo = atmos[0]
                atmos.pop(0)

            room.atmo = atmo
            room.color = color
            

