import colorsys
import pygame
import random

class MapVisualizer:
    def __init__(self, game_manager, game_map, player):
        self.game_manager = game_manager
        self.game_map = game_map
        self.player = player
        self.cell_size = 25  # Size of each cell
        self.border_width = 2  # Width of the border around each room
        self.connection_size = self.cell_size // 3  # Size of the connections
        self.padding = 2  # Padding around the map
        self.region_color_mapping, self.region_colors = self.generate_region_colors()
        self.explored = set() 
        self.explored.add((player.x, player.y))

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

    def draw_map(self, screen, offset_x = 0):
        visibility_radius = 3 # default 3, + 2 with torch
        self.update_light_levels(visibility_radius)
        enemy_positions = {(enemy.x, enemy.y) for enemy in self.game_manager.enemy_manager.enemies}
        for room in self.game_map.rooms.values():
            x = room.x * (self.cell_size + self.connection_size) + self.padding + offset_x
            y = room.y * (self.cell_size + self.connection_size) + self.padding
            room_pos = (room.x, room.y)
            if room.lit > 0:
                region_index = self.region_color_mapping.get(room.region, 0)
                base_room_color = self.region_colors[region_index]
                room_color = self.get_color_intensity(base_room_color, room.lit)
                if room_pos == (self.player.x, self.player.y):
                    pygame.draw.rect(screen, (255, 0, 0), (x-2, y-2, self.cell_size+4, self.cell_size+4), 2)
                    room_color = (0, 0, 255)  # Player's room
                elif room_pos in enemy_positions:
                    base_enemy_color = (255, 0, 0)  # Enemy's room
                    room_color = self.get_color_intensity(base_enemy_color, room.lit)
                self.draw_connectionless_edges(screen, room, x, y)
            else:
                room_color = (0, 0, 0)
            pygame.draw.rect(screen, room_color, (x, y, self.cell_size, self.cell_size))
            for direction, connected_room in room.connections.items():
                if connected_room and (connected_room.x, connected_room.y) in self.explored:
                    self.draw_connection(screen, x, y, direction)
            # Draw an asterisk in the room if it has decorations
            if len(room.decorations) > 0 and room.lit > 0:
                asterisk_font = pygame.font.Font(None, 12)  # Choose an appropriate font size
                symbol = "*"
                asterisk_surface = asterisk_font.render(symbol, True, (200, 200, 200))  # White asterisk
                asterisk_rect = asterisk_surface.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                screen.blit(asterisk_surface, asterisk_rect.topleft)

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
            connection_rect = (x - self.connection_size, y + self.cell_size / 3, self.connection_size, self.connection_size)
        elif direction == 'n':  # North
            connection_rect = (x + self.cell_size / 3, y - self.connection_size, self.connection_size, self.connection_size)
        pygame.draw.rect(screen, (150, 150, 150), connection_rect)
    
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