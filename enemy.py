class Enemy:
    def __init__(self, start_room):
        self.x, self.y = start_room.x, start_room.y
        self.current_room = start_room
        self.current_room.enemies.append(self)
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
        self.speed = 2
        self.aggro = False
        self.is_following_player = False
    
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
        if distance <= 3:
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
        # Initialize open and closed sets
        open_set = {start_room}
        closed_set = set()
        # Initialize scores and parents
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
        return []  # No path found

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