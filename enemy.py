import random

class Enemy:
    def __init__(self, start_room, level):
        self.name = "" # generated when spawned
        self.exp = 30
        self.x, self.y = start_room.x, start_room.y
        self.current_room = start_room
        self.speed = 2
        self.current_room.enemies.append(self)
        self.in_combat = False
        self.level = max(level, 1)  # Ensure level is at least 1
        self.atk = 10
        self.defn = 10
        self.int = 10
        self.wis = 10
        self.con = 10
        self.eva = 10
        self.max_hp = 50
        self.max_mp = 10
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.stats = {"level": self.level, "atk": self.atk, "defn": self.defn, "int": self.int, "wis": self.wis, "con": self.con, "eva": self.eva, "max_hp": self.max_hp}
        self.aggro = False
        self.is_following_player = False
        self.aggro = False
        self.is_following_player = False
        self.initialize_stats_based_on_level()
        
    def initialize_stats_based_on_level(self):
        for _ in range(1, self.level):
            self.atk += round(random.randint(2, 6))  # Reduced from 5-10
            self.defn += round(random.randint(1, 3))  # Reduced from 2-4
            self.int += round(random.randint(2, 6))  # Reduced from 5-10
            self.wis += round(random.randint(1, 3))  # Reduced from 2-5
            self.con += round(random.randint(2, 7))  # Reduced from 5-13
            self.eva += round(random.randint(1, 3))  # Reduced from 2-5
            self.max_hp += round((self.con * random.randint(1, 2)))  # Reduced multiplier
            self.max_mp += round(random.randint(1, 2))  # Reduced from 1-3
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.stats = {"level": self.level, "atk": self.atk, "defn": self.defn, "int": self.int, "wis": self.wis, "con": self.con, "eva": self.eva, "max_hp": self.max_hp}
        
    def move_to_room(self, new_room):
        self.x, self.y = new_room.x, new_room.y
        self.current_room.enemies.remove(self)
        self.current_room = new_room
        self.current_room.enemies.append(self)
    
    def can_move(self, direction, game_map):
        current_room = game_map.rooms[(self.x, self.y)]
        if direction in current_room.connections and current_room.connections[direction] is not None:
            return True
        return False
    
    def check_aggro(self, player_x, player_y):
        distance = ((self.x - player_x) ** 2 + (self.y - player_y) ** 2) ** 0.5
        if distance <= 5: # all enemies see you before you see them, unless you have the best light source; then it's even
            self.aggro = True
        else:
            self.aggro = False

    def find_path_to_player(self, player, game_map):
        path = self.a_star(self.current_room, player.current_room, game_map)
        return path

    def next_move_on_path(self, path):
        if path:
            next_room = path.pop(0)
            return next_room
        return None
    
    def a_star(self, start_room, target_room, game_map):
        open_set = {start_room}
        closed_set = set()
        g_score = {room: float('inf') for room in game_map.rooms.values()}
        f_score = {room: float('inf') for room in game_map.rooms.values()}
        parent = {room: None for room in game_map.rooms.values()}
        g_score[start_room] = 0
        f_score[start_room] = self.calculate_heuristic(start_room, target_room)
        while open_set:
            current = min(open_set, key=lambda room: f_score[room])
            if current == target_room:
                return self.reconstruct_path(parent, current)
            open_set.remove(current)
            closed_set.add(current)
            for direction, neighbor in current.connections.items():
                if neighbor in closed_set or neighbor is None:
                    continue
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score[neighbor]:
                    parent[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.calculate_heuristic(neighbor, target_room)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
        return []

    def calculate_heuristic(self, room_a, room_b):
        # Example using Manhattan distance
        return abs(room_a.x - room_b.x) + abs(room_a.y - room_b.y)

    def reconstruct_path(self, parent, current):
        path = []
        while current and parent[current] is not None:  # Exclude the starting room
            path.append(current)
            current = parent[current]
        path.reverse()
        return path

    def log_stats(self):
        stats = (
            f"Level: {self.level}, "
            f"Attack: {self.atk}, "
            f"Defense: {self.defn}, "
            f"Intelligence: {self.int}, "
            f"Wisdom: {self.wis}, "
            f"Constitution: {self.con}, "
            f"Evasion: {self.eva}, "
            f"HP: {self.hp}, "
            f"MP: {self.mp}"
        )
        print(f"Enemy Stats ({self.name}):", stats)