import random
import json
from collections import deque

class MapNamer:
    def __init__(self, map_instance, words_file):
        self.map = map_instance
        self.map_size = len(self.map.rooms)
        self.locations = self.load_locations(words_file)
        self.assign_regions()

    def load_locations(self, words_file):
        with open(words_file, 'r') as file:
            data = json.load(file)
        return data['locations']

    def assign_regions(self):
        unassigned_rooms = set(self.map.rooms.keys())
        regions = list(self.locations.items())
        
        while unassigned_rooms:
            random.shuffle(regions)  # Shuffle the list of regions
            for region, data in regions:
                if not unassigned_rooms:
                    break
                region_size = self.calculate_region_size(data['total_zones'])
                self.assign_region_to_rooms(region, region_size, data['zone_names'], unassigned_rooms)

    def select_random_region(self):
        return random.choice(list(self.locations.items()))

    def calculate_region_size(self, total_zones):
        variance = round(total_zones * 0.2)
        return random.randint(max(1, total_zones - variance), total_zones + variance)

    def assign_region_to_rooms(self, region, size, zone_names, unassigned_rooms):
        shuffled_zone_names = zone_names[:]
        random.shuffle(shuffled_zone_names)
        zone_name_index = 0

        start_room_pos = random.choice(list(unassigned_rooms))
        region_rooms = self.create_continuous_blob(start_room_pos, size, unassigned_rooms)

        for pos in region_rooms:
            room = self.map.rooms[pos]
            region = region.replace('_', ' ')
            room.region = region.title()
            room.name = shuffled_zone_names[zone_name_index]

            zone_name_index += 1
            if zone_name_index >= len(shuffled_zone_names):
                # Reshuffle and start over if we've used all zone names
                random.shuffle(shuffled_zone_names)
                zone_name_index = 0

    def create_continuous_blob(self, start_pos, size, unassigned_rooms):
        blob = set()
        queue = deque([start_pos])
        while queue and len(blob) < size:
            current_pos = queue.popleft()
            if current_pos in unassigned_rooms:
                unassigned_rooms.remove(current_pos)
                blob.add(current_pos)
                for neighbor_pos in self.get_adjacent_positions(current_pos):
                    if neighbor_pos in unassigned_rooms:
                        queue.append(neighbor_pos)
        return blob

    def get_adjacent_positions(self, pos):
        x, y = pos
        return [(x + dx, y + dy) for dx, dy in [(0, -1), (0, 1), (1, 0), (-1, 0)] if (x + dx, y + dy) in self.map.rooms]

    def list_rooms_by_region(self):
        room_info = []
        for pos, room in self.map.rooms.items():
            room_info.append((room.region, pos, room.name))

        room_info.sort(key=lambda x: x[0])  # Sort by region
        return room_info
    
    def get_map_size(self):
        return len(map.rooms)
    
    def count_regions(self):
        region_counts = {}
        for room in self.map.rooms.values():
            if room.region not in region_counts:
                region_counts[room.region] = 0
            region_counts[room.region] += 1
        return region_counts