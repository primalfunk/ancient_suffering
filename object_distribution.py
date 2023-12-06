import json
import random

class ObjectDistribution:
    def __init__(self, map_instance):
        self.map = map_instance
        with open('words.json', 'r') as file:
            object_data = json.load(file)["objects"]
            self.tool_data = object_data["tools"]  # Two of each tool
            self.weapon_data = random.sample(object_data["weapons"], 3)  # Three random weapons
            self.armor_data = random.sample(object_data["armor"], 3)  # Three random armor pieces
            self.artifact_data = random.sample(object_data["artifacts"], 1)  # One random artifact
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
        possible_positions = [pos for pos in self.map.rooms if len(self.map.rooms[pos].decorations) == 0]
        random.shuffle(possible_positions)
        for item in self.all_items:
            if possible_positions:
                room_pos = possible_positions.pop()
                self.map.rooms[room_pos].decorations.append(item)

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