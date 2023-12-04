import json
import random

class RoomDecoration:
    def __init__(self, map_instance, decoration_data):
        self.map = map_instance
        self.decorations_data = decoration_data

    def decorate_rooms(self):
        decorated_rooms_count = 0
        total_rooms = len(self.map.rooms)
        target_decorated_rooms = int(total_rooms * 0.3)
        for pos, room in self.map.rooms.items():
            if decorated_rooms_count >= target_decorated_rooms:
                break
            room_type = self.determine_room_type(room.region)
            room.decorations = self.select_decorations_for_room(room_type)
            if room.decorations:
                decorated_rooms_count += 1

    def determine_room_type(self, region):
        # Logic to determine the type of room based on the region
        if region in ('town,' 'castle', 'village', 'mansion', 'neighborhood', 'metropolis'):
            return 'urban'
        elif region in ('forest', 'plains', 'coastline', 'jungle', 'woods', 'meadow', 'marshlands', 'steppe', 'tree', 'garden'):
            return 'outdoor'
        elif region in ('magical', 'enchanted', 'elven', 'crystal', 'ancient'):
            return 'magical-type'
        elif region is None:
            return 'any'
        else:
            return 'any'

    def select_decorations_for_room(self, room_type):
        # Decide whether to add a group-specific or general item
        group_specific_chance = 0.5 if room_type in ['urban', 'outdoor', 'magical-type'] else 0.25
        if random.random() < group_specific_chance:
            # Select a group-specific item
            decoration = self.get_group_specific_item(room_type)
        else:
            # Select a general item based on remaining probabilities
            decoration = self.get_general_item()

        return [decoration] if decoration else []

    def get_group_specific_item(self, room_type):
        if room_type == 'urban':
            return self.get_random_item('furniture')
        elif room_type == 'outdoor':
            return self.get_random_item('wildlife') or self.get_random_item('natural_elements')
        elif room_type == 'magical-type':
            return self.get_random_item('mystic_items')
        return None

    def get_general_item(self):
        # 75% for daily_life_items, 15% for artifacts, 10% for mystic_items
        random_choice = random.random()
        if random_choice < 0.75:
            return self.get_random_item('daily_life_items')
        elif random_choice < 0.90:
            return self.get_random_item('artifacts')
        else:
            return self.get_random_item('mystic_items')
        
    def get_random_item(self, category):
        # Randomly select one item from a category
        items = self.decorations_data['objects'][category]
        if items:
            return random.choice(items)
        return None