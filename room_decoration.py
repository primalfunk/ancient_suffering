import json
import random

class RoomDecoration:
    def __init__(self, map_instance, decoration_data):
        self.map = map_instance
        self.decorations_data = decoration_data
        self.decorate_rooms()
        # self.visualize_decorations()

    def decorate_rooms(self):
        for pos, room in self.map.rooms.items():
            if random.random() < 0.2:
                room_type = self.determine_room_type(room.region)
                room.decorations = self.select_decorations_for_room(room_type)

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
        if random.random() < 0.25:
            decoration = self.get_group_specific_item(room_type)
        else:
            decoration = self.get_random_item('daily_life_items')
        return [decoration] if decoration else []
                
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

    def visualize_decorations(self):
        map_width = max(x for x, _ in self.map.rooms.keys()) + 1
        map_height = max(y for _, y in self.map.rooms.keys()) + 1

        decoration_summary = {'F': 0, 'T': 0, 'N': 0, 'A': 0, 'W': 0, 'M': 0, 'D': 0}

        for y in range(map_height):
            for x in range(map_width):
                room = self.map.rooms.get((x, y))
                if room:
                    if room.decorations:
                        decoration = room.decorations[0]
                        decoration_category = self.get_decoration_category(decoration)
                        decoration_letter = decoration_category[0].upper()
                        print(decoration_letter, end='')
                        decoration_summary[decoration_letter] += 1
                    else:
                        print('x', end='')  # Room without decoration
                else:
                    print(' ', end='')  # No room
            print()  # New line after each row

        print("\nDecoration Summary:")
        for category, count in decoration_summary.items():
            print(f"{category}: {count}")


    def get_decoration_category(self, decoration):
        for category, items in self.decorations_data['objects'].items():
            if decoration in items:
                return category
        return 'unknown'