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
        print(f"start room is {start_room}, room name is {start_room.name}")
        self.player = Player(start_room)
        self.player_move_count = 0
        self.enemies = []
        self.spawn_enemies(10)
        self.map_visualizer = MapVisualizer(self, game_map, self.player)
        # Calculate window size based on map size, connection size, and padding
        cell_size = 30
        connection_size = cell_size // 3
        padding = 10
        window_size = game_map.size * cell_size + (game_map.size - 1) * connection_size + padding * 2
        self.window_width = window_size
        self.window_height = window_size + 160
        self.window_width *= 2
        # Create the Pygame window
        self.screen = pygame.display.set_mode([self.window_width, self.window_height])
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
            self.player_move_count += 1
            new_room = self.game_map.rooms[(self.player.x, self.player.y)].connections[direction]
            self.player.move_to_room(new_room)
            self.map_visualizer.explored.add((new_room.x, new_room.y))
            self.map_visualizer.update_light_levels(visibility_radius=3)
        else:
            print("You can't go that way.")

    def move_enemies(self):
        for enemy in self.enemies:
            if self.player_move_count % enemy.speed == 0:
                if random.random() < 0.87:  # 87% chance to move
                    self.move_enemy(enemy)

    def move_enemy(self, enemy):
        if enemy.aggro:
            # Chase player logic
            direction = self.calculate_direction_towards_player(enemy, self.player)
        else:
            # Random movement logic
            valid_directions = [dir for dir in ['n', 's', 'e', 'w'] if enemy.can_move(dir, self.game_map)]
            direction = random.choice(valid_directions) if valid_directions else None

        if direction:
            new_room = self.game_map.rooms[(enemy.x, enemy.y)].connections[direction]
            enemy.move_to_room(new_room)

    def spawn_enemies(self, count):
        for _ in range(count):  # Spawn count enemies
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
    
    def update_enemies_aggro(self):
        player_x, player_y = self.player.x, self.player.y
        for enemy in self.enemies:
            enemy.check_aggro(player_x, player_y)
            if enemy.aggro:
                print("Aggro!")

    def calculate_direction_towards_player(self, enemy, player):
        best_direction = None
        min_distance = float('inf')

        for direction in ['n', 's', 'e', 'w']:
            if enemy.can_move(direction, self.game_map):
                dx, dy = self.direction_to_delta(direction)
                new_x, new_y = enemy.x + dx, enemy.y + dy
                distance = ((new_x - player.x) ** 2 + (new_y - player.y) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    best_direction = direction
        return best_direction

    def direction_to_delta(self, direction):
        return {
            'n': (0, -1),
            's': (0, 1),
            'e': (1, 0),
            'w': (-1, 0)
        }.get(direction, (0, 0))
    
    def display_room_info(self):
        room_info_surface = pygame.Surface((self.window_width // 2, self.window_height))
        room_info_surface.fill((0, 0, 0))
        # Set custom font and render room name
        custom_font = pygame.font.Font('customfont.ttf', 20)

        room_name = self.player.current_room.name
        text_surface = custom_font.render(room_name, True, (255, 255, 255))  # White text
        room_info_surface.blit(text_surface, (10, 10))  # Position text with padding
        # Draw a light green border around the room_info_surface
        border_color = (144, 238, 144)  # Light green color
        border_width = 1  # Border thickness
        pygame.draw.rect(room_info_surface, border_color, room_info_surface.get_rect(), border_width)
        # Blit the room info surface onto the main screen, on the left side
        self.screen.blit(room_info_surface, (0, 0))

    def display_player_stats(self):
        custom_font = pygame.font.Font('customfont.ttf', 20)
        stats_surface = pygame.Surface((self.window_height - 160, 160))
        stats_surface.fill((50, 50, 50))
        first_column_attributes = ['name', 'level', 'hp', 'mp', 'exp']
        second_column_attributes = ['str', 'dex', 'int', 'wis', 'con', 'cha']
        third_column_attributes = ['x', 'y']
        for i, attr in enumerate(first_column_attributes):
            color = (170, 190, 255)
            text = f"{attr.upper()}: {getattr(self.player, attr)}"
            text_surface = custom_font.render(text, True, color)
            stats_surface.blit(text_surface, (10, 20 * i))
        # Render second column
        column_offset = self.window_width // 3  # Horizontal offset for the second column
        for i, attr in enumerate(second_column_attributes):
            text = f"{attr.upper()}: {getattr(self.player, attr)}"
            text_surface = custom_font.render(text, True, (170, 190, 255))  # White text
            stats_surface.blit(text_surface, (column_offset, 20 * i))
        # Render third column
        column_offset = 2 * self.window_width // 3 # Horizontal offset for the second column
        for i, attr in enumerate(third_column_attributes):
            if attr == 'x':
                text = f"LATITUDE: {getattr(self.player, attr)}"
            elif attr == 'y':
                text = f"LONGITUDE: {getattr(self.player, attr)}"
            else:
                text = f"{attr.upper()}: {getattr(self.player, attr)}"
            text_surface = custom_font.render(text, True, (170, 190, 255))  # White text
            stats_surface.blit(text_surface, (column_offset, 20 * i))
        # Blit the stats surface onto the main screen
        half_window_width = self.window_width // 2
        self.screen.blit(stats_surface, (half_window_width, self.window_height - 160))

    def run_game_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_player_movement(event)
                    self.move_enemies()
                    self.update_enemies_aggro()

            self.screen.fill((0, 0, 0))
            self.display_room_info()
            half_window_width = self.window_width // 2
            self.map_visualizer.draw_map(self.screen, offset_x=half_window_width)
            self.display_player_stats()
            pygame.display.flip()