from collections import deque
from map_elaborator import MapElaborator
import random
from room import Room


class Map:
    def __init__(self, size):
        self.size = size
        self.rooms = {}
        self.connections = {}
        self.populate_grid()
        self.generate_map()
        MapElaborator(self, 'words.json')

    def generate_map(self):
        self.populate_grid()
        self.irregularize_outline()
        self.create_holes()
        self.ensure_connectivity() 
        self.remove_invalid_connections()

    def create_holes(self):
        max_holes = self.size // 5
        hole_radius = self.size // 10
        for _ in range(max_holes):
            center_x = random.randint(hole_radius, self.size - hole_radius)
            center_y = random.randint(hole_radius, self.size - hole_radius)
            for x in range(center_x - hole_radius, center_x + hole_radius):
                for y in range(center_y - hole_radius, center_y + hole_radius):
                    if (x - center_x)**2 + (y - center_y)**2 <= hole_radius**2:
                        self.rooms.pop((x, y), None)

    def create_room(self, pos):
        room_id = len(self.rooms) + 1
        room = Room(room_id, *pos)
        self.rooms[pos] = room
        return room

    def ensure_connectivity(self):
        # Choose any room as the starting point
        start = next(iter(self.rooms.values()))
        visited = set()
        self.dfs(start, visited)
        if len(visited) != len(self.rooms):
            for room in set(self.rooms.values()) - visited:
                self.reconnect_room(room)

    def dfs(self, room, visited):
        if room in visited:
            return
        visited.add(room)
        for direction, next_room in room.connections.items():
            if next_room in self.rooms and next_room not in visited:
                self.dfs(next_room, visited)

    def reconnect_room(self, room):
        # Check all adjacent rooms and connect to the closest valid room
        for dx, dy in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
            adjacent_pos = (room.x + dx, room.y + dy)
            if adjacent_pos in self.rooms:
                self.establish_connection(room, self.rooms[adjacent_pos])
                break  # Stop after connecting to one valid room

    def establish_initial_connections(self):
        start = next(iter(self.rooms.values()))  # Start from any room
        self.randomized_dfs(start, None, 0)

    def randomized_dfs(self, current_room, previous_direction, straight_path_count, visited=None):
        if visited is None:
            visited = set()
        visited.add(current_room)
        directions = ['n', 'e', 's', 'w']
        random.shuffle(directions)  # Randomize the direction order
        for direction in directions:
            next_room = self.get_adjacent_room(current_room, direction)
            if next_room and next_room not in visited:
                new_straight_path_count = straight_path_count + 1 if direction == previous_direction else 0
                if new_straight_path_count <= 4:
                    self.establish_connection(current_room, next_room)
                    self.randomized_dfs(next_room, direction, new_straight_path_count, visited)

    def get_adjacent_room(self, room, direction):
        dx, dy = {'n': (0, -1), 's': (0, 1), 'e': (1, 0), 'w': (-1, 0)}.get(direction, (0, 0))
        adjacent_pos = (room.x + dx, room.y + dy)
        return self.rooms.get(adjacent_pos)

    def establish_connection(self, room1, room2):
        direction = None
        opposite_direction = None
        if room1.x == room2.x:
            if room1.y < room2.y:
                direction, opposite_direction = 's', 'n'
            else:
                direction, opposite_direction = 'n', 's'
        elif room1.y == room2.y:
            if room1.x < room2.x:
                direction, opposite_direction = 'e', 'w'
            else:
                direction, opposite_direction = 'w', 'e'
        if direction and opposite_direction:
            self.connections.setdefault(room1.room_id, {})[direction] = room2.room_id
            self.connections.setdefault(room2.room_id, {})[opposite_direction] = room1.room_id
            room1.connect(direction, room2)
            room2.connect(opposite_direction, room1)

    def find_nearest_connected_room(self, unconnected_room):
        queue = deque([unconnected_room])
        visited = set([unconnected_room])
        while queue:
            current_room = queue.popleft()
            for neighbor in self.get_adjacent_rooms(current_room):
                if neighbor in visited:
                    continue
                if neighbor in self.rooms.values():  # Check if neighbor is a connected room
                    return neighbor
                visited.add(neighbor)
                queue.append(neighbor)
        return None

    def get_adjacent_rooms(self, room):
        neighbors = {'n': None, 's': None, 'e': None, 'w': None}
        for direction, (dx, dy) in {'n': (0, -1), 's': (0, 1), 'e': (1, 0), 'w': (-1, 0)}.items():
            adjacent_pos = (room.x + dx, room.y + dy)
            if adjacent_pos in self.rooms:
                neighbors[direction] = self.rooms[adjacent_pos]
        return neighbors

    def irregularize_outline(self):
        edges = [
            [(x, 0) for x in range(self.size)],
            [(x, self.size - 1) for x in range(self.size)],
            [(0, y) for y in range(self.size)],
            [(self.size - 1, y) for y in range(self.size)]
        ]
        for edge in edges:
            self.remove_edge_segments(edge)

    def populate_grid(self):
        for x in range(self.size):
            for y in range(self.size):
                self.create_room((x, y))
        self.establish_initial_connections() 

    def remove_edge_segments(self, edge):
        segment_length = random.randint(2, self.size // 4)  # Random segment length
        start = 0
        while start < len(edge):
            if random.random() < 0.5:  # 50% chance to remove a segment
                for pos in edge[start:start + segment_length]:
                    self.rooms.pop(pos, None)
            start += segment_length

    def remove_invalid_connections(self):
        for room in self.rooms.values():
            for direction in list(room.connections.keys()):
                connected_room = room.connections[direction]
                if connected_room not in self.rooms.values():
                    # Remove the invalid connection
                    room.connections[direction] = None
