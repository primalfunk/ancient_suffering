import random

class Enemy:
    def __init__(self, start_room, level):
        self.name = ""
        self.xp_reward = 30 # default
        self.x, self.y = start_room.x, start_room.y
        self.current_room = start_room
        self.speed = 2
        self.current_room.enemies.append(self)
        self.level = max(level, 1)
        self.max_hp = 30
        self.hp = self.max_hp
        self.aggro = False
        self.in_combat = False
        self.is_following_player = False
        self.initialize_stats_based_on_level()
        
    def initialize_stats_based_on_level(self):
        self.atk = 10
        self.defn = 10
        self.int = 1
        self.wis = 1
        self.con = 1
        self.eva = 1
        self.exp = 30
        self.hp = 50
        self.mp = 10
        self.max_hp = 50
        self.max_mp = 10
        for level in range(1, self.level):
            self.atk += max(1, level + random.randint(0, 2))
            self.defn += max(1, level + random.randint(0, 2))
            self.max_hp += (2 * level) + random.randint(0, 2)
        self.hp = self.max_hp
        
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
        # enemies always see you before you see them, or at worst, at the same time; can't be snuck up on
        distance = ((self.x - player_x) ** 2 + (self.y - player_y) ** 2) ** 0.5
        if distance <= 5:
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