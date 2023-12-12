import colorsys
import pygame
import random

class MapVisualizer:
    def __init__(self, game_manager, game_map, player, screen_width):
        self.screen = game_manager.screen
        self.game_manager = game_manager
        self.game_map = game_map
        self.player = player
        self.grid_width_in_cells = self.game_map.size
        self.border_width = 2
        self.padding = 2
        # Adjust for additional 10px constraint in both width and height
        additional_constraint = 10
        max_available_width = screen_width / 2 - additional_constraint
        max_available_height = game_manager.screen_height - additional_constraint

        # Use the smaller of the adjusted width or height for cell size calculation
        max_dimension = min(max_available_width, max_available_height)
        total_padding = 2 * self.padding

        # Calculate cell_size considering the smaller dimension
        self.cell_size = int((max_dimension - total_padding) / ((4/3 * self.game_map.size) - 1/3))
        self.connection_size = self.cell_size // 3
        self.region_color_mapping, self.region_colors = self.generate_region_colors()
        self.dead_ends = [room for room in self.game_map.rooms.values() if sum(1 for conn in room.connections.values() if conn) == 1]
        self.explored = set() 
        self.explored.add((player.x, player.y))
        self.max_light_level = 5
        self.max_lit = len(self.game_map.rooms) * self.max_light_level
        self.current_lit = self.calculate_percent_lit()
        self.x_offset = self.game_manager.map_area_x

    def get_color_intensity(self, base_color, light_level, max_light_level=5):
        factor = light_level / max_light_level  # Normalizes the light level
        adjusted_color = tuple(min(int(c * factor), 255) for c in base_color)
        return adjusted_color
        
    def update_light_levels(self, visibility_radius):
        current_player_room = self.game_map.rooms.get((self.player.x, self.player.y))
        if current_player_room:
            current_player_room.lit = 5
        for dx in range(-visibility_radius, visibility_radius + 1):
            for dy in range(-visibility_radius, visibility_radius + 1):
                # Skip the player's current location
                if dx == 0 and dy == 0:
                    continue
                distance = self.calculate_distance(0, 0, dx, dy)
                if distance <= visibility_radius:
                    room = self.game_map.rooms.get((self.player.x + dx, self.player.y + dy))
                    if room:
                        light_level = min(5 - int(distance), 4)
                        room.lit = max(room.lit, light_level)
    
    def draw_map(self, screen):
        if self.player.has_map:
            for room in self.game_map.rooms.values():
                room.lit = self.max_light_level
        elif self.player.visibility_radius_changed:
            self.update_light_levels(self.player.visibility_radius)
        enemy_positions = {(enemy.x, enemy.y) for enemy in self.game_manager.enemy_manager.enemies}
        
        for room in self.game_map.rooms.values():
            x = room.x * (self.cell_size + self.connection_size) + self.padding + self.x_offset
            y = room.y * (self.cell_size + self.connection_size) + self.padding
            room_pos = (room.x, room.y)
            if room.lit > 0:
                region_index = self.region_color_mapping.get(room.region, 0)
                base_room_color = self.region_colors[region_index]
                base_dead_end_color = (155, 155, 0) # color for dead ends with items in them
                room_color = self.get_color_intensity(base_room_color, room.lit)
                if room_pos == (self.player.x, self.player.y):
                    pygame.draw.rect(screen, (0, 255, 0), (x-2, y-2, self.cell_size+4, self.cell_size+4), 2) # Player's border
                    room_color = (0, 0, 255)  # Player's room
                elif room_pos in enemy_positions:
                    base_enemy_color = (255, 0, 0)  # Enemy's room
                    room_color = self.get_color_intensity(base_enemy_color, room.lit)
                elif room in self.dead_ends and len(room.decorations) > 0:
                    room_color = self.get_color_intensity(base_dead_end_color, room.lit)
                self.draw_connectionless_edges(screen, room, x, y)
            else:
                room_color = (0, 0, 0)
            pygame.draw.rect(screen, room_color, (x, y, self.cell_size, self.cell_size))
            if room.lit > 0:
                smaller_rect_x = x + self.cell_size / 8
                smaller_rect_y = y + self.cell_size / 8
                smaller_rect_size = 3 * self.cell_size / 4
                lighter_room_color = self.lighten_color(room_color)
                pygame.draw.rect(screen, lighter_room_color, (smaller_rect_x, smaller_rect_y, smaller_rect_size, smaller_rect_size))
                for direction, connected_room in room.connections.items():
                    if connected_room and (connected_room.x, connected_room.y) in self.explored:
                        self.draw_connection(screen, x, y, direction, room_color)

    def draw_all_connections(self):
        for room in self.game_map.rooms.values():
            self.explored.add((room.x, room.y))

    def get_room_color(self, room):
        region_index = self.region_color_mapping.get(room.region, 0)
        base_room_color = self.region_colors[region_index]
        return self.get_color_intensity(base_room_color, room.lit)
    
    def draw_connection(self, screen, x, y, direction, color):
        # Factor to control the size of the connection
        connection_dimension = self.cell_size * 0.5
        if direction == 'e':  # East
            connection_rect = (x + self.cell_size, y + self.cell_size / 2 - connection_dimension / 2, self.connection_size, connection_dimension)
        elif direction == 's':  # South
            connection_rect = (x + self.cell_size / 2 - connection_dimension / 2, y + self.cell_size, connection_dimension, self.connection_size)
        elif direction == 'w':  # West
            connection_rect = (x - self.connection_size, y + self.cell_size / 2 - connection_dimension / 2, self.connection_size, connection_dimension)
        elif direction == 'n':  # North
            connection_rect = (x + self.cell_size / 2 - connection_dimension / 2, y - self.connection_size, connection_dimension, self.connection_size)
        pygame.draw.rect(screen, color, connection_rect)
    
    def draw_connectionless_edges(self, screen, room, x, y):
        border_color = (30, 30, 30)  # Dark color
        border_width = 5
        if 'n' not in room.connections or room.connections['n'] is None:
            pygame.draw.line(screen, border_color, (x, y), (x + self.cell_size, y), border_width)
        if 's' not in room.connections or room.connections['s'] is None:
            pygame.draw.line(screen, border_color, (x, y + self.cell_size), (x + self.cell_size, y + self.cell_size), border_width)
        if 'e' not in room.connections or room.connections['e'] is None:
            pygame.draw.line(screen, border_color, (x + self.cell_size, y), (x + self.cell_size, y + self.cell_size), border_width)
        if 'w' not in room.connections or room.connections['w'] is None:
            pygame.draw.line(screen, border_color, (x, y), (x, y + self.cell_size), border_width)

    def calculate_distance(self, x1, y1, x2, y2):
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def update_light_levels(self, visibility_radius):
        self.explored.add((self.player.x, self.player.y))
        max_light_level = 5

        for dx in range(-visibility_radius, visibility_radius + 1):
            for dy in range(-visibility_radius, visibility_radius + 1):
                distance = self.calculate_distance(0, 0, dx, dy)
                if distance <= visibility_radius:
                    room = self.game_map.rooms.get((self.player.x + dx, self.player.y + dy))
                    if room:
                        # Adjust light level based on distance and visibility radius
                        if distance == 0:
                            light_level = max_light_level
                        elif visibility_radius in [3, 4] and distance == 1:
                            light_level = visibility_radius - 1
                        else:
                            light_level = 1

                        room.lit = max(room.lit, light_level)

    def calculate_percent_lit(self):
        total_lit = 0
        for room in self.game_map.rooms.values():
            total_lit += room.lit
        return round(100 * total_lit / self.max_lit, 2)

    def generate_region_colors(self):
        unique_regions = list(set(room.region for room in self.game_map.rooms.values()))
        num_regions = len(unique_regions)
        region_color_mapping = {region: i for i, region in enumerate(unique_regions)}
        colors = [self.adjusted_hsv_to_rgb(i / num_regions) for i in range(num_regions)]
        return region_color_mapping, colors

    def hsv_to_rgb(self, h, s, v):
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(r * 255), int(g * 255), int(b * 255)

    def adjusted_hsv_to_rgb(self, hue_fraction):
        base_hue = (hue_fraction * 0.6) + 0.2  # Avoids red and blue
        hue_variance = 0.05
        hue = base_hue + random.uniform(-hue_variance, hue_variance)
        hue = max(0.0, min(hue, 1.0))  # Ensure hue stays within [0, 1]
        saturation = random.uniform(0.4, 0.6)  # Adjust these ranges as needed
        value = random.uniform(0.6, 0.8)
        return self.hsv_to_rgb(hue, saturation, value)
    
    def lighten_color(self, color):
        lighten_factor = 0.025  # Adjust as needed
        return tuple(min(255, int(c + lighten_factor * 255)) for c in color)