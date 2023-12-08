from collections import deque
import logging
import random
from room import Room

class RoomConnector:
    def __init__(self, map):
        self.connector_logger = logging.getLogger('connector')
        self.map = map
        self.connections = {}
        self.rooms = self.map.rooms
        self.establish_initial_connections()
        self.ensure_connectivity()
        self.reduce_dead_ends()
        self.remove_invalid_connections()

    def get_adjacent_room(self, room, direction):
        if isinstance(room, Room):
            dx, dy = {'n': (0, -1), 's': (0, 1), 'e': (1, 0), 'w': (-1, 0)}.get(direction, (0, 0))
            adjacent_pos = (room.x + dx, room.y + dy)
            return self.rooms.get(adjacent_pos)
        else:
            self.connector_logger.error(f"Expected Room object, got {type(room)} instead.")

    def get_adjacent_rooms(self, room):
        if not isinstance(room, Room):
            self.connector_logger.error(f"get_adjacent_rooms: Expected Room, got {type(room)}")
            return []
        neighbors = {'n': None, 's': None, 'e': None, 'w': None}
        for direction, (dx, dy) in {'n': (0, -1), 's': (0, 1), 'e': (1, 0), 'w': (-1, 0)}.items():
            adjacent_pos = (room.x + dx, room.y + dy)
            if adjacent_pos in self.rooms:
                neighbors[direction] = self.rooms[adjacent_pos]
        return neighbors.values()
    
    def get_potential_connections(self, room):
        potential_connections = []
        for direction in ['n', 's', 'e', 'w']:
            if not room.connections[direction]:
                adjacent_room = self.get_adjacent_room(room, direction)
                if adjacent_room:
                    potential_connections.append((adjacent_room, direction))
        return potential_connections

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

    def establish_connection(self, room1, room2):
        direction = None
        opposite_direction = None
        if room1 == room2:
            self.connector_logger.error(f"Attempted to connect room {room1.room_id} to itself.")
            return
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
        self.connector_logger.debug(f"Established connection between room {room1.room_id} and {room2.room_id}")

    def find_nearest_connected_room(self, unconnected_room):
        self.connector_logger.debug(f"Finding nearest connected room for unconnected room ID {unconnected_room.room_id}")
        queue = deque([unconnected_room])
        visited = set([unconnected_room])
        while queue:
            current_room = queue.popleft()
            for neighbor in self.get_adjacent_rooms(current_room):
                if neighbor in visited or neighbor is None:
                    continue
                if neighbor in self.rooms.values():
                    self.connector_logger.debug(f"Nearest connected room for room ID {unconnected_room.room_id} is {neighbor.room_id}")
                    return neighbor
                visited.add(neighbor)
                queue.append(neighbor)
        self.connector_logger.warning(f"No connected room found for room ID {unconnected_room.room_id}")
        return None

    def ensure_connectivity(self):
        # Start with BFS from a random room
        start = next(iter(self.rooms.values()))
        visited = set()
        queue = deque([start])

        while queue:
            current_room = queue.popleft()
            if current_room not in visited:
                visited.add(current_room)
                for direction, next_room in current_room.connections.items():
                    if next_room and next_room not in visited:
                        queue.append(next_room)

        # Connect any remaining unconnected rooms
        for room in self.rooms.values():
            if room not in visited:
                nearest_connected_room = self.find_nearest_connected_room(room)
                if nearest_connected_room:
                    self.establish_connection(room, nearest_connected_room)
                    queue.append(room)  # Add room to queue for BFS
                    visited.add(room)  # Mark room as visited

        # Check if all rooms are now connected
        self.remove_unconnected_rooms()
        assert len(visited) == len(self.rooms), "Map is still not fully connected."

    def dfs(self, room, visited):
        if room in visited:
            return
        visited.add(room)
        for direction, next_room in room.connections.items():
            if next_room in self.rooms and next_room not in visited:
                if not isinstance(next_room, Room):
                    self.connector_logger.error(f"dfs: next_room is not a Room object: {next_room}")
                    continue
                self.dfs(next_room, visited)

    def remove_invalid_connections(self):
        for room in self.rooms.values():
            for direction in list(room.connections.keys()):
                connected_room = room.connections[direction]
                if connected_room not in self.rooms.values():
                    # Remove the invalid connection
                    room.connections[direction] = None

    def reduce_dead_ends(self):
        # Identify dead end rooms
        dead_end_rooms = [room for room in self.rooms.values() if sum(1 for conn in room.connections.values() if conn) == 1]
        self.connector_logger.debug(f"Starting dead end count is {len(dead_end_rooms)}")
        target_count = len(dead_end_rooms) - 11 * 2 # exactly 11 dead-ends; one of each of the three tools (backpack, lantern, bedroll), three weapons, three armors, one random artifact, and one 'key' room we'll use later 

        for room in random.sample(dead_end_rooms, min(target_count, len(dead_end_rooms))):
            # Identify potential new connections
            potential_connections = self.get_potential_connections(room)

            if potential_connections:
                new_connection, _ = random.choice(potential_connections)  # Unpack the tuple
                self.establish_connection(room, new_connection)

        dead_end_rooms = [room for room in self.rooms.values() if sum(1 for conn in room.connections.values() if conn) == 1]
        self.connector_logger.debug(f"Ending dead end count is {len(dead_end_rooms)}")

    def remove_unconnected_rooms(self):
        unconnected_rooms = [room_id for room_id, room in self.rooms.items() if not room.connections]
        for room_id in unconnected_rooms:
            self.connector_logger.info(f"Removing unconnected room: {room_id}")
            del self.rooms[room_id]