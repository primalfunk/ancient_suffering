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
        self.map_visualizer = MapVisualizer(game_map, self.player)

        # Calculate window size based on map size, connection size, and padding
        cell_size = 30
        connection_size = cell_size // 3
        padding = 10
        window_size = game_map.size * cell_size + (game_map.size - 1) * connection_size + padding * 2

        # Create the Pygame window
        self.screen = pygame.display.set_mode([window_size, window_size])
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

    def run_game_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_player_movement(event)  # Ensure this is being called

            self.screen.fill((0, 0, 0))  # Set background to black
            self.map_visualizer.draw_map(self.screen)
            pygame.display.flip()