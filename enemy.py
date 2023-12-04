class Enemy:
    def __init__(self, start_room):
        self.x, self.y = start_room.x, start_room.y
        self.name = "Enemy"
        self.str = 0
        self.dex = 0
        self.int = 0
        self.wis = 0
        self.con = 0
        self.cha = 0
        self.exp = 30 # experience reward for player
        self.level = 0
        self.hp = 30
        self.mp = 10
        self.speed = 2 # count of player moves required before this character moves
        self.aggro = False

    def move_to_room(self, new_room):
        self.x, self.y = new_room.x, new_room.y

    def can_move(self, direction, game_map):
        current_room = game_map.rooms[(self.x, self.y)]
        if direction in current_room.connections and current_room.connections[direction] is not None:
            return True
        return False
    
    def check_aggro(self, player_x, player_y):
        distance = ((self.x - player_x) ** 2 + (self.y - player_y) ** 2) ** 0.5
        if distance <= 3:
            self.aggro = True
        else:
            self.aggro = False