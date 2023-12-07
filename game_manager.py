from combat import Combat
from enemy_manager import EnemyManager
import logging
from map import Map
from map_visualizer import MapVisualizer
from player import Player
import pygame
import random
from ui import UI

# Configure logging
logging.basicConfig(filename='boot.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class GameManager:
    def __init__(self, screen):
        self.game_map = Map(25) # instantiate the Map
        cell_size = 25
        connection_size = cell_size // 3
        padding = 2
        window_size = self.game_map.size * cell_size + (self.game_map.size - 1) * connection_size + padding * 2
        self.window_width = window_size
        self.window_height = window_size + 160
        self.window_width *= 2
        self.screen = pygame.display.set_mode([self.window_width, self.window_height])
        self.combat = None
        self.staggered_enemies = False
        self.player_move_count = 0
        self.is_combat = False
        self.fade_in_done = False
        self.screen = screen
        self.fullscreen = True
        start_room = random.choice(list(self.game_map.rooms.values()))
        self.player = Player(start_room) # instantiate the Player
        self.enemy_manager = EnemyManager(self.game_map, self.player, self.player_move_count) # instantiate the EnemyManager
        self.map_visualizer = MapVisualizer(self, self.game_map, self.player) # instantiate the MapVisualizer
        pygame.display.set_caption("Journey to a Finished Game")
        self.current_state = "title_screen"
        self.ui = UI(self.screen, self.player, self.window_width, self.window_height, self)

    def move_player(self, direction):
        if direction and self.player.can_move(direction, self.game_map):
            cardinals = {"n": "north",
                         "s": "south",
                         "w": "west",
                         "e": "east"}
            cardinal_direction = cardinals[direction]
            self.player_move_count += 1
            new_room = self.game_map.rooms[(self.player.x, self.player.y)].connections[direction]
            self.player.move_to_room(new_room)
            self.map_visualizer.explored.add((new_room.x, new_room.y))
            self.map_visualizer.update_light_levels(visibility_radius=3)
            new_region_name = new_room.region.replace('_', ' ')
            self.ui.message_display.add_message(f"Travelled {cardinal_direction} to {new_room.name.lower()} ({new_room.x}, {new_room.y})")
            # call the method here to change the text of the ui.middle_button
        else:
            self.ui.message_display.add_message(f"You can't go that way.")

    def update(self):
        # Update game state for a single frame
        self.screen.fill((0, 0, 0))
        self.ui.room_display.display_room_info(self.screen)
        self.ui.update_ui()
        half_window_width = self.window_width // 2
        self.map_visualizer.draw_map(self.screen, offset_x=half_window_width)
        self.check_for_combat()
        pygame.display.flip()

    def direction_to_delta(self, direction):
        return {
            'n': (0, -1),
            's': (0, 1),
            'e': (1, 0),
            'w': (-1, 0)
        }.get(direction, (0, 0))
    
    def restart_game(self):
        # Reinitialize the Map, Player, EnemyManager, UI, etc.
        logging.debug("Restarting game...")
        logging.debug("Creating the Map...")
        start_room = random.choice(list(self.game_map.rooms.values()))
        self.player = Player(start_room)
        self.player_move_count = 0
        self.enemy_manager = EnemyManager(self.game_map, self.player, self.player_move_count)
        self.map_visualizer = MapVisualizer(self, self.game_map, self.player)
        self.ui = UI(self.screen, self.player, self.window_width, self.window_height, self)
        logging.debug("Game restarted successfully.")

    def process_keypress(self, event):
        direction = None
        if event.key == pygame.K_UP:
            direction = 'n'
        elif event.key == pygame.K_DOWN:
            direction = 's'
        elif event.key == pygame.K_LEFT:
            direction = 'w'
        elif event.key == pygame.K_RIGHT:
            direction = 'e'
        elif event.key == pygame.K_SPACE:
            # check the middle button text
            if self.ui.middle_button_label == "Pick Up":
                self.ui.handle_middle_button_click()
        elif event.key == pygame.K_q:
            pygame.quit()
            exit(0)  # Quit the game
        if direction:
            self.move_player(direction)
            self.enemy_manager.move_enemies()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            pygame.display.set_mode((self.window_width, self.window_height), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((self.window_width, self.window_height))

    def draw_initial_ui_onto_surface(self, surface):
        # Draw the room information onto fade_surface
        self.ui.room_display.display_room_info(surface)
        self.ui.render_player_stats(surface)
        # Draw the lower part of the UI onto fade_surface
        lower_ui_surface = pygame.Surface((self.window_width // 2, self.window_height // 4))
        lower_ui_surface.fill((0, 0, 0))
        padding = 10
        self.ui.render_middle_button_and_inventory_frame(lower_ui_surface, padding)
        self.ui.render_direction_buttons(lower_ui_surface, padding)
        border_color = (144, 238, 144)
        pygame.draw.rect(lower_ui_surface, border_color, lower_ui_surface.get_rect(), 2)
        surface.blit(lower_ui_surface, (0, self.window_height * 3 // 4))
        # Draw player stats and message display onto fade_surface
        self.ui.message_display.render(surface)
        # Draw the map onto fade_surface
        half_window_width = self.window_width // 2
        self.map_visualizer.draw_map(surface, offset_x=half_window_width)

    def check_for_combat(self):
        self.is_combat = self.player.in_combat
        return self.is_combat
