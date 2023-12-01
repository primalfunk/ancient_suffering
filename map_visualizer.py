import pygame

class MapVisualizer:
    def __init__(self, game_manager, game_map, player):
        self.game_manager = game_manager
        self.game_map = game_map
        self.player = player
        self.cell_size = 30  # Size of each cell
        self.border_width = 2  # Width of the border around each room
        self.connection_size = self.cell_size // 3  # Size of the connections
        self.padding = 10  # Padding around the map
        self.explored = set() 
        self.explored.add((player.x, player.y))

    def draw_map(self, screen):
        visibility_radius = 3
        self.update_light_levels(visibility_radius)
        enemy_positions = {(enemy.x, enemy.y) for enemy in self.game_manager.enemies}

        for room in self.game_map.rooms.values():
            x = room.x * (self.cell_size + self.connection_size) + self.padding
            y = room.y * (self.cell_size + self.connection_size) + self.padding
            room_pos = (room.x, room.y)

            # Check if room is within visibility radius
            if room.lit > 0:
                if room_pos == (self.player.x, self.player.y):
                    room_color = (0, 0, 255)  # Blue color for player's room
                elif room_pos in enemy_positions:
                    # Apply gradient effect for enemy rooms based on light level
                    base_enemy_color = (255, 0, 0)  # Red color for enemy rooms
                    room_color = self.get_color_intensity(base_enemy_color, room.lit)
                else:
                    # Apply gradient effect for normal rooms based on light level
                    base_room_color = (173, 216, 230)  # Light blue for normal rooms
                    room_color = self.get_color_intensity(base_room_color, room.lit)
            else:
                room_color = (0, 0, 0)  # Default color for unexplored/hidden rooms


            pygame.draw.rect(screen, room_color, (x, y, self.cell_size, self.cell_size))

            # Draw connections if the connected room is explored
            for direction, connected_room in room.connections.items():
                if connected_room and (connected_room.x, connected_room.y) in self.explored:
                    self.draw_connection(screen, x, y, direction)

    def update_light_levels(self, visibility_radius):
        for dx in range(-visibility_radius, visibility_radius + 1):
            for dy in range(-visibility_radius, visibility_radius + 1):
                distance = self.calculate_distance(0, 0, dx, dy)
                if distance <= visibility_radius:
                    room = self.game_map.rooms.get((self.player.x + dx, self.player.y + dy))
                    if room:
                        light_level = visibility_radius - int(distance)
                        room.lit = max(room.lit, light_level)

    def draw_connection(self, screen, x, y, direction):
        if direction == 'e':  # East
            connection_rect = (x + self.cell_size, y + self.cell_size / 3, self.connection_size, self.connection_size)
        elif direction == 's':  # South
            connection_rect = (x + self.cell_size / 3, y + self.cell_size, self.connection_size, self.connection_size)
        elif direction == 'w':  # West
            # Align the right edge of the connection with the left edge of the cell
            connection_rect = (x - self.connection_size, y + self.cell_size / 3, self.connection_size, self.connection_size)
        elif direction == 'n':  # North
            # Align the bottom edge of the connection with the top edge of the cell
            connection_rect = (x + self.cell_size / 3, y - self.connection_size, self.connection_size, self.connection_size)
        pygame.draw.rect(screen, (150, 150, 150), connection_rect)
    
    def calculate_distance(self, x1, y1, x2, y2):
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def update_light_levels(self, visibility_radius):
        self.explored.add((self.player.x, self.player.y))
        for dx in range(-visibility_radius, visibility_radius + 1):
            for dy in range(-visibility_radius, visibility_radius + 1):
                distance = self.calculate_distance(0, 0, dx, dy)
                if distance <= visibility_radius:
                    room = self.game_map.rooms.get((self.player.x + dx, self.player.y + dy))
                    if room:
                        light_level = visibility_radius - int(distance)
                        room.lit = max(room.lit, light_level)
    
    def get_color_intensity(self, base_color, light_level):
        factor = light_level / 3  # Assuming 3 is the max light level
        adjusted_color = tuple(int(c * factor) for c in base_color)
        return adjusted_color