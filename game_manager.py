from enemy_manager import EnemyManager
import logging
from map import Map
from map_visualizer import MapVisualizer
from player import Player
import pygame
import random
from sound_manager import SoundManager
from ui import UI

class GameManager:
    def __init__(self, screen, width, height):
        self.size = 25
        self.boot_logger = logging.getLogger('boot')
        self.game_map = Map(self.size)
        self.screen = screen
        self.width = width
        self.height = height
        self.screen_width = width
        self.map_area_x = self.screen_width // 2
        self.screen_height = height
        self.combat = None
        self.staggered_enemies = False
        self.player_move_count = 0
        self.is_combat = False
        self.fade_in_done = False
        self.screen = screen
        self.fullscreen = True
        start_room = random.choice(list(self.game_map.rooms.values()))
        self.player = Player(start_room, self)
        self.enemy_manager = EnemyManager(self.game_map, self.player, self.player_move_count)
        self.map_visualizer = MapVisualizer(self, self.game_map, self.player, self.width)
        self.map_visualizer.update_light_levels(self.player.visibility_radius)
        pygame.display.set_caption("The Lords of Chaos")
        self.current_state = "title_screen"
        self.light_change = False
        self.ui = UI(self.screen, self.player, self.screen_width, self.screen_height, self)
        self.sounds = SoundManager()

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
            self.map_visualizer.update_light_levels(self.player.visibility_radius)
            self.sounds.play_sound('travel', 0.5)
            self.ui.message_display.add_message(f"Travelled {cardinal_direction} to {new_room.name.title()} ({new_room.x}, {new_room.y})")
            # condition for reaching the target room
            if self.player.current_room.is_target:
                self.victory_conditions()
        else:
            self.ui.message_display.add_message(f"You can't go that way.")

    def victory_conditions(self):
        # Reset the game map and enemies, clear inventory
        self.player.inventory.items = []
        self.game_map = Map(self.size)
        for room in self.game_map.rooms.values():
            room.lit = 0
        start_room = random.choice(list(self.game_map.rooms.values()))
        self.player.current_room = start_room
        self.player_move_count = 0
        self.enemy_manager = EnemyManager(self.game_map, self.player, self.player_move_count)
        self.map_visualizer = MapVisualizer(self, self.game_map, self.player, self.width)
        self.map_visualizer.update_light_levels(self.player.visibility_radius)
        self.ui = UI(self.screen, self.player, self.screen_width, self.screen_height, self)

    def update(self):
        # Update game state for a single frame
        self.screen.fill((0, 0, 0))
        self.ui.room_display.display_room_info(self.screen)
        self.ui.update_ui()
        self.map_area_x = self.screen_width // 2
        self.map_visualizer.draw_map(self.screen)
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
        self.boot_logger.debug("Restarting game...")
        self.game_map = Map(self.size)
        for room in self.game_map.rooms.values():
            room.lit = 0 
        start_room = random.choice(list(self.game_map.rooms.values()))
        self.player = Player(start_room, self)
        self.player_move_count = 0
        self.enemy_manager = EnemyManager(self.game_map, self.player, self.player_move_count)
        self.map_visualizer = MapVisualizer(self, self.game_map, self.player, self.width)
        self.map_visualizer.update_light_levels(self.player.visibility_radius)
        self.ui = UI(self.screen, self.player, self.screen_width, self.screen_height, self)
        self.boot_logger.debug("Game restarted successfully.")

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
            if self.ui.middle_button_label in ("Pick Up", "Attack"):
                self.ui.handle_middle_button_click()
        elif event.key == pygame.K_q:
            self.sounds.play_sound('gameover', 0.75)
            pygame.time.wait(750)
            pygame.quit()
            exit(0)  # Quit the game
        if direction:
            self.move_player(direction)
            self.enemy_manager.move_enemies()            

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((self.screen_width, self.screen_height))

    def draw_initial_ui_onto_surface(self, surface):
        self.ui.room_display.display_room_info(surface)
        self.ui.render_player_stats(surface)
        lower_ui_surface = pygame.Surface((self.screen_width // 2, self.screen_height // 4))
        lower_ui_surface.fill((0, 0, 0))
        padding = 10
        self.ui.render_middle_button_and_inventory_frame(lower_ui_surface, padding)
        self.ui.render_direction_buttons(lower_ui_surface, padding)
        border_color = (144, 238, 144)
        pygame.draw.rect(lower_ui_surface, border_color, lower_ui_surface.get_rect(), 2)
        surface.blit(lower_ui_surface, (0, self.screen_height * 3 // 4))
        self.ui.message_display.render(surface)
        self.map_visualizer.draw_map(surface)
        self.ui.draw_hp_bar()

    def check_for_combat(self):
        self.is_combat = self.player.in_combat
        return self.is_combat
