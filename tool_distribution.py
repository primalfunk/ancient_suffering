import random

class ToolDistribution:
    def __init__(self, map_instance, tool_data):
        self.map = map_instance
        self.tools = tool_data
        self.distribute_tools()

    def distribute_tools(self):
        # Calculate the dimensions of the map
        map_width = max(x for x, _ in self.map.rooms.keys()) + 1
        map_height = max(y for _, y in self.map.rooms.keys()) + 1

        # Divide the map into four quadrants
        quadrants = self.divide_map_into_quadrants(map_width, map_height)

        # Distribute one tool per quadrant
        for tool, quadrant in zip(self.tools, quadrants.values()):
            possible_positions = [pos for pos in quadrant if pos in self.map.rooms]
            if possible_positions:
                room_pos = random.choice(possible_positions)
                if self.map.rooms[room_pos].decorations is None:
                    self.map.rooms[room_pos].decorations = []
                self.map.rooms[room_pos].decorations.append(tool)

    def divide_map_into_quadrants(self, map_width, map_height):
        mid_x, mid_y = map_width // 2, map_height // 2
        quadrants = {
            'top_left': [(x, y) for x in range(mid_x) for y in range(mid_y)],
            'top_right': [(x, y) for x in range(mid_x, map_width) for y in range(mid_y)],
            'bottom_left': [(x, y) for x in range(mid_x) for y in range(mid_y, map_height)],
            'bottom_right': [(x, y) for x in range(mid_x, map_width) for y in range(mid_y, map_height)]
        }
        return quadrants
    
    def visualize_tool_distribution(self):
        map_width = max(x for x, _ in self.map.rooms.keys()) + 1
        map_height = max(y for _, y in self.map.rooms.keys()) + 1
        
        for y in range(map_height):
            for x in range(map_width):
                if (x, y) in self.map.rooms:
                    room = self.map.rooms[(x, y)]
                    if any(tool in room.decorations for tool in self.tools):
                        print('O', end=' ')
                    else:
                        print('x', end=' ')
                else:
                    print(' ', end=' ')
            print()  # New line after each row