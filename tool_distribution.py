import random

class ToolDistribution:
    def __init__(self, map_instance, tool_data):
        self.map = map_instance
        self.tools = tool_data

    def distribute_tools(self):
        tools = self.tools
        quadrants = self.divide_map_into_quadrants()
        for quadrant_name, quadrant_positions in quadrants.items():
            if not tools:  # Break if there are no more tools to distribute
                break
            room_pos = self.select_random_room_from_quadrant(quadrant_positions)
            tool = tools.pop(0)  # Remove the first tool from the list
            # Ensure the room's decorations attribute is initialized
            if self.map.rooms[room_pos].decorations is None:
                self.map.rooms[room_pos].decorations = []
            self.map.rooms[room_pos].decorations.append(tool)

    def divide_map_into_quadrants(self):
        map_width = max(x for x, _ in self.map.rooms.keys()) + 1
        map_height = max(y for _, y in self.map.rooms.keys()) + 1
        mid_x, mid_y = map_width // 2, map_height // 2

        # Define the four quadrants
        quadrants = {
            'top_left': [(x, y) for x in range(mid_x) for y in range(mid_y) if (x, y) in self.map.rooms],
            'top_right': [(x, y) for x in range(mid_x, map_width) for y in range(mid_y) if (x, y) in self.map.rooms],
            'bottom_left': [(x, y) for x in range(mid_x) for y in range(mid_y, map_height) if (x, y) in self.map.rooms],
            'bottom_right': [(x, y) for x in range(mid_x, map_width) for y in range(mid_y, map_height) if (x, y) in self.map.rooms]
        }

        return quadrants
    
    def select_random_room_from_quadrant(self, quadrant):
        return random.choice(quadrant)