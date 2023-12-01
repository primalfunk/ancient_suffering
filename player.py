class Player:
    def __init__(self, start_room):
        self.x, self.y = start_room.x, start_room.y
        self.name = "PLAYER"
        self.str = 0 # strength
        self.dex = 0 # dexterity
        self.int = 0 # intelligence
        self.wis = 0 # wisdom
        self.con = 0 # constitution
        self.cha = 0 # charisma
        self.exp = 0 # experience
        self.level = 0
        self.hp = 50
        self.mp = 10

    def move_to_room(self, new_room):
        self.x, self.y = new_room.x, new_room.y

    def can_move(self, direction, game_map):
        current_room = game_map.rooms[(self.x, self.y)]
        if direction in current_room.connections and current_room.connections[direction] is not None:
            return True
        return False