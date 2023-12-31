import logging
from map_elaborator import MapElaborator
import random
from room import Room
from room_connector import RoomConnector

class Map:
    def __init__(self, size):
        self.map_logger = logging.getLogger('map')
        self.size = size
        self.rooms = {}
        self.rooms_with_keys = []
        self.generate_map()
        MapElaborator(self, 'words.json')

    def generate_map(self):
        attempt = 0
        max_attempts = 10
        while attempt < max_attempts:
            try:
                self.populate_grid()
                self.irregularize_outline()
                self.visualize_map()
                self.room_connector = RoomConnector(self)
                break  # Exit loop if no assertion error
            except AssertionError:
                self.map_logger.error(f"Map generation failed on attempt {attempt + 1}. Retrying...")
                self.rooms.clear()  # Clear the current map
                attempt += 1
        if attempt == max_attempts:
            raise RuntimeError("Failed to generate a valid map after maximum attempts.")

    def create_room(self, pos):
        room_id = len(self.rooms) + 1
        room = Room(room_id, *pos, self)
        self.rooms[pos] = room
        self.map_logger.debug(f"Created room with ID: {room_id} at position {pos}")
        return room

    def reconnect_room(self, room):
        # Check all adjacent rooms and connect to the closest valid room
        for dx, dy in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
            adjacent_pos = (room.x + dx, room.y + dy)
            if adjacent_pos in self.rooms:
                self.room_connector.establish_connection(room, self.rooms[adjacent_pos])
                break  # Stop after connecting to one valid room

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

    def remove_edge_segments(self, edge):
        segment_length = random.randint(2, self.size // 4)  # Random segment length
        start = 0
        while start < len(edge):
            if random.random() < 0.5:  # 50% chance to remove a segment
                for pos in edge[start:start + segment_length]:
                    self.rooms.pop(pos, None)
            start += segment_length

    def visualize_map(self):
        map_str = ''
        for y in range(self.size):
            row_str = ''
            for x in range(self.size):
                room = self.rooms.get((x, y))
                row_str += 'X' if room else ' '
            map_str += row_str + '\n'
        return map_str