import pygame

class MapVisualizer:
    def __init__(self, game_map, player):
        self.game_map = game_map
        self.player = player
        self.cell_size = 30  # Size of each cell
        self.border_width = 2  # Width of the border around each room
        self.connection_size = self.cell_size // 3  # Size of the connections
        self.padding = 10  # Padding around the map

    def draw_map(self, screen):
        for room in self.game_map.rooms.values():
            # Adjust x and y coordinates to include padding
            x = room.x * (self.cell_size + self.connection_size) + self.padding
            y = room.y * (self.cell_size + self.connection_size) + self.padding

            # Draw room border
            pygame.draw.rect(screen, (0, 0, 0), 
                            (x - self.border_width, y - self.border_width, 
                             self.cell_size + self.border_width * 2, self.cell_size + self.border_width * 2))

            # Draw room
            pygame.draw.rect(screen, (173, 216, 230),  # Light blue color
                            (x, y, self.cell_size, self.cell_size))

            # Draw the player's current location in red
            player_x, player_y = self.player.x, self.player.y
            px = player_x * (self.cell_size + self.connection_size) + self.padding
            py = player_y * (self.cell_size + self.connection_size) + self.padding
            pygame.draw.rect(screen, (255, 0, 0), (px, py, self.cell_size, self.cell_size))

            # Draw connections
            if room.connections.get('e'):
                pygame.draw.rect(screen, (0, 0, 0),
                                (x + self.cell_size, y + self.cell_size / 3, 
                                 self.connection_size, self.connection_size))
            if room.connections.get('s'):
                pygame.draw.rect(screen, (0, 0, 0),
                                (x + self.cell_size / 3, y + self.cell_size, 
                                 self.connection_size, self.connection_size))
