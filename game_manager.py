from enemy import Enemy
from player import Player
import pygame
import random
from map_visualizer import MapVisualizer

class GameManager:
    def __init__(self, game_map):
        # Initialize Pygame
        pygame.init()
        # Set up the game map and visualizer
        self.game_map = game_map
        start_room = random.choice(list(game_map.rooms.values()))
        self.player = Player(start_room)
        self.enemies = []
        self.spawn_enemies(5)
        self.map_visualizer = MapVisualizer(self, game_map, self.player)
        # Calculate window size based on map size, connection size, and padding
        cell_size = 30
        connection_size = cell_size // 3
        padding = 10
        window_size = game_map.size * cell_size + (game_map.size - 1) * connection_size + padding * 2
        self.window_height = window_size + 160

        # Create the Pygame window
        self.screen = pygame.display.set_mode([window_size, self.window_height])
        pygame.display.set_caption("Map Visualization")

    def handle_player_movement(self, event):
        direction = None
        if event.key == pygame.K_UP:
            direction = 'n'
        elif event.key == pygame.K_DOWN:
            direction = 's'
        elif event.key == pygame.K_LEFT:
            direction = 'w'
        elif event.key == pygame.K_RIGHT:
            direction = 'e'
        if direction and self.player.can_move(direction, self.game_map):
            new_room = self.game_map.rooms[(self.player.x, self.player.y)].connections[direction]
            self.player.move_to_room(new_room)
            self.map_visualizer.explored.add((new_room.x, new_room.y))
            self.map_visualizer.update_light_levels(visibility_radius=3)
        else:
            print("You can't go that way.")

    def display_player_stats(self):
        stats_font = pygame.font.SysFont("Arial", 20)
        stats_surface = pygame.Surface((self.window_height - 160, 160))
        stats_surface.fill((50, 50, 50))  # Dark gray background for the stats area

        # Attributes for the first and second columns
        first_column_attributes = ['name', 'level', 'hp', 'mp', 'exp']
        second_column_attributes = ['str', 'dex', 'int', 'wis', 'con', 'cha']
        third_column_attributes = ['x', 'y']

        # Render first column
        for i, attr in enumerate(first_column_attributes):
            text = f"{attr.upper()}: {getattr(self.player, attr)}"
            text_surface = stats_font.render(text, True, (255, 255, 255))  # White text
            stats_surface.blit(text_surface, (10, 20 * i))

        # Render second column
        column_offset = 180  # Horizontal offset for the second column
        for i, attr in enumerate(second_column_attributes):
            text = f"{attr.upper()}: {getattr(self.player, attr)}"
            text_surface = stats_font.render(text, True, (255, 255, 255))  # White text
            stats_surface.blit(text_surface, (column_offset, 20 * i))

        # Render third column
        column_offset = 360  # Horizontal offset for the second column
        for i, attr in enumerate(third_column_attributes):
            text = f"{attr.upper()}: {getattr(self.player, attr)}"
            text_surface = stats_font.render(text, True, (255, 255, 255))  # White text
            stats_surface.blit(text_surface, (column_offset, 20 * i))

        # Blit the stats surface onto the main screen
        self.screen.blit(stats_surface, (0, self.window_height - 160))

    def run_game_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_player_movement(event)
            self.screen.fill((0, 0, 0))
            self.map_visualizer.draw_map(self.screen)
            self.display_player_stats() 
            pygame.display.flip()

    def spawn_enemies(self, count):
        for _ in range(count):  # Spawn 5 enemies
            while True:
                potential_start = random.choice(list(self.game_map.rooms.values()))
                if self.is_valid_spawn(potential_start):
                    enemy = Enemy(potential_start)
                    self.enemies.append(enemy)
                    break
        print(f"Spawned enemies: {self.enemies}")

    def is_valid_spawn(self, start_room):
        # Check distance from player and other enemies
        for other in [self.player] + self.enemies:
            if abs(start_room.x - other.x) <= 5 and abs(start_room.y - other.y) <= 5:
                return False
        return True