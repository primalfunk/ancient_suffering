from collections import deque
import logging
import math
import random

class RegionAssignment:
    def __init__(self, map_instance, location_data):
        self.map_logger = logging.getLogger('map')
        self.map = map_instance
        self.locations = location_data
        self.assign_regions()
        self.adjust_region_borders()

    def assign_regions(self):
        unassigned_rooms = set(self.map.rooms.keys())
        shuffled_regions = list(self.locations.items())
        random.shuffle(shuffled_regions)

        for region, data in shuffled_regions:
            if data['total_zones'] > len(unassigned_rooms):
                self.map_logger.warning(f"Total zones for region {region} exceed unassigned rooms. Limiting to available rooms.")
                data['total_zones'] = len(unassigned_rooms)

            while unassigned_rooms and data['total_zones'] > 0:
                start_pos = random.choice(list(unassigned_rooms))
                grown_size = self.grow_region(start_pos, region, unassigned_rooms, data['total_zones'])
                data['total_zones'] -= grown_size

    def grow_region(self, start_pos, region, unassigned_rooms, max_size):
        queue = deque([start_pos])
        grown_size = 0

        while queue and grown_size < max_size:
            current_pos = queue.popleft()
            if current_pos in unassigned_rooms:
                self.assign_room(current_pos, region, unassigned_rooms)
                grown_size += 1

                for neighbor_pos in self.get_adjacent_positions(current_pos):
                    if neighbor_pos in unassigned_rooms:
                        queue.append(neighbor_pos)

        return grown_size

    def assign_room(self, pos, region, unassigned_rooms):
        room = self.map.rooms[pos]
        room.region = region
        room.name = random.choice(self.locations[region]['zone_names'])
        unassigned_rooms.remove(pos)

    def adjust_region_borders(self):
        unassigned_rooms = {pos for pos, room in self.map.rooms.items() if room.region is None}
        iteration_count = 0
        while unassigned_rooms:
            for pos in list(unassigned_rooms):
                self.adjust_room_region(pos, unassigned_rooms)
            iteration_count += 1
            if iteration_count > len(self.map.rooms):
                self.map_logger.warning("Infinite loop detected in adjust_region_borders. Breaking out of loop.")
                break

    def adjust_room_region(self, pos, unassigned_rooms):
        neighbors = self.get_adjacent_positions(pos)
        best_region = None
        max_neighbors = 0
        for neighbor_pos in neighbors:
            neighbor_room = self.map.rooms.get(neighbor_pos)
            if neighbor_room and neighbor_room.region:
                count = self.count_region_neighbors(neighbor_pos, neighbor_room.region)
                if count > max_neighbors:
                    max_neighbors = count
                    best_region = neighbor_room.region
        if best_region:
            room = self.map.rooms[pos]
            room.region = best_region
            room.name = random.choice(self.locations[best_region]['zone_names'])
            unassigned_rooms.remove(pos)

    def count_region_neighbors(self, pos, region):
        count = 0
        for neighbor_pos in self.get_adjacent_positions(pos):
            neighbor_room = self.map.rooms.get(neighbor_pos)
            if neighbor_room and neighbor_room.region == region:
                count += 1
        return count

    def get_adjacent_positions(self, pos):
        x, y = pos
        adjacent_positions = []
        if (x, y - 1) in self.map.rooms:
            adjacent_positions.append((x, y - 1))
        if (x, y + 1) in self.map.rooms:
            adjacent_positions.append((x, y + 1))
        if (x + 1, y) in self.map.rooms:
            adjacent_positions.append((x + 1, y))
        if (x - 1, y) in self.map.rooms:
            adjacent_positions.append((x - 1, y))
        return adjacent_positions

    def visualize_map(self, map_instance):
        map_width, map_height = self.calculate_map_dimensions(map_instance)
        for y in range(map_height):
            for x in range(map_width):
                room = map_instance.rooms.get((x, y))
                if room:
                    if room.region:
                        self.map_logger.info(f"{room.region[0].upper()}", end='')
                    else:
                        self.map_logger.info(f"X", end='')
                else:
                    self.map_logger.info(" ", end='')  # Two spaces for empty areas
            self.map_logger.info()  # Newline after each row

    def calculate_map_dimensions(self, map_instance):
        total_rooms = len(map_instance.rooms)
        map_width = int(math.sqrt(total_rooms))
        map_height = math.ceil(total_rooms / map_width)
        return map_width, map_height