import json
import logging
import random

class RoomDecoration:
    def __init__(self, map_instance, decoration_data):
        self.map_logger = logging.getLogger('map')
        self.map = map_instance
        self.decorations_data = decoration_data
        self.adjectives = self.load_adjectives()
        self.decorate_rooms()

    def decorate_rooms(self):
        for pos, room in self.map.rooms.items():
            if len(room.decorations) == 0 and random.random() < 0.33:
                room_type = self.determine_room_type(room.region)
                decoration = self.select_decorations_for_room(room_type)
                if decoration:
                    adjective = random.choice(self.adjectives)
                    decorated_name = f"{adjective} {decoration}"
                    room.decorations = [decorated_name]

    def determine_room_type(self, region):
        if region in ("clockwork_city", "coastal_town", "farming_village", "suburban_neighborhood", "downtown_city", "haunted_mansion", "cyberpunk_city", "steampunk_metropolis", "pirate_haven", "abandoned_city", "treetop_village", "frostbound_village"):
            return 'urban'
        elif region in ("fiery_chasm", "nomadic_steppe", "frozen_wasteland", "volcanic_valley", "cursed_woods", "mirage_oasis", "labyrinth_gardens", "pine_forest", "dense_jungle", "quiet_lake", "grassy_plains", "mountain_campsite", "forest"):
            return 'outdoor'
        elif region in ("enchanted_forest", "crystal_caves", "mushroom_kingdom", "enchanted_valley", "crystal_canyon", "wizards_academy", "dwarven_kingdom", "ancient_temple", "magical_menagerie"):
            return 'magical'
        else:
            return 'any'

    def select_decorations_for_room(self, room_type):
        if random.random() < 0.13:
            decoration = self.get_group_specific_item(room_type)
        else:
            decoration = self.get_random_item('daily_life_items')
        return decoration if decoration else ""
                
    def get_group_specific_item(self, room_type):
        if room_type == 'urban':
            return self.get_random_item('furniture')
        elif room_type == 'outdoor':
            return random.choice([self.get_random_item('wildlife'), self.get_random_item('natural_elements')])
        elif room_type == 'magical':
            return self.get_random_item('mystic_items')
        return None

    def get_random_item(self, category):
        items = self.decorations_data['objects'][category]
        if items:
            selected_item = random.choice(items)
            return selected_item
        return None

    def get_decoration_category(self, decoration):
        for category, items in self.decorations_data['objects'].items():
            if decoration in items:
                return category
        return 'unknown'
    
    def load_adjectives(self):
            with open('words.json') as file:
                data = json.load(file)
            return data["adjectives"]["things"]