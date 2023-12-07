import json
import random

class ObjectDistribution:
    def __init__(self, map_instance):
        self.map = map_instance
        self.placement_rooms = [room for room in self.map.rooms.values() if sum(1 for conn in room.connections.values() if conn) == 1]
        print(f"ObjectDistribution received {len(self.placement_rooms)} placement spots, needs 11.")
        if len(self.placement_rooms) < 11:
            print(f"Not enough rooms for placement.")
        with open('words.json', 'r') as file:
            object_data = json.load(file)["objects"]
            self.tool_data = object_data["tools"]  # One of each tool
            self.weapon_data = random.sample(object_data["weapons"], 3)  # Three random weapons
            self.armor_data = random.sample(object_data["armor"], 3)  # Three random armor pieces
            self.artifact_data = random.sample(object_data["artifacts"], 1)  # One random artifact
            # and space for one last one, the key area where the artifact is activated
        self.all_items = self.tool_data + self.weapon_data + self.armor_data + self.artifact_data
        random.shuffle(self.all_items)
        self.distribute_items()
        # self.visualize_object_distribution()

    def get_category_letter(self, item):
        if item in self.tool_data:
            return 'T'
        elif item in self.weapon_data:
            return 'W'
        elif item in self.armor_data:
            return 'A'
        elif item in self.artifact_data:
            return 'K'
        return ""
    
    def distribute_items(self):
        # Shuffle the placement rooms to randomize item distribution
        random.shuffle(self.placement_rooms)
        for item in self.all_items:
            if self.placement_rooms:
                room = self.placement_rooms.pop()
                room.decorations.append(item)

    def visualize_object_distribution(self):
        map_width = max(x for x, _ in self.map.rooms.keys()) + 1
        map_height = max(y for _, y in self.map.rooms.keys()) + 1
        for y in range(map_height):
            for x in range(map_width):
                if (x, y) in self.map.rooms:
                    room = self.map.rooms[(x, y)]
                    if room.decorations:
                        print(self.get_category_letter(room.decorations[0]), end=' ')
                    else:
                        print('x', end=' ')
                else:
                    print(' ', end=' ')
            print()

    def is_item_pickable(self, item):
        category_letter = self.get_category_letter(item)
        return category_letter in {'T', 'W', 'A', 'K'} 