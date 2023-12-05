from enemy import Enemy
from player import Player
import pygame
import random
from map_visualizer import MapVisualizer
from ui import UI

class GameManager:
    def __init__(self, game_map):
        pygame.init()
        self.game_map = game_map
        start_room = random.choice(list(game_map.rooms.values()))
        self.player = Player(start_room)
        self.player_move_count = 0
        self.enemies = []
        self.spawn_enemies(10)
        self.map_visualizer = MapVisualizer(self, game_map, self.player)
        cell_size = 25
        connection_size = cell_size // 3
        padding = 2
        window_size = game_map.size * cell_size + (game_map.size - 1) * connection_size + padding * 2
        self.window_width = window_size
        self.window_height = window_size + 160
        self.window_width *= 2
        self.screen = pygame.display.set_mode([self.window_width, self.window_height])
        pygame.display.set_caption("Journey to a Finished Game")
        self.ui = UI(self.screen, self.player, self.window_width, self.window_height, self)

    def move_player(self, direction):
        if direction and self.player.can_move(direction, self.game_map):
            self.player_move_count += 1
            new_room = self.game_map.rooms[(self.player.x, self.player.y)].connections[direction]
            self.player.move_to_room(new_room)
            self.map_visualizer.explored.add((new_room.x, new_room.y))
            self.map_visualizer.update_light_levels(visibility_radius=3)
        else:
            print("You can't go that way.")

    def run_game_loop(self):
        running = True
        while running:
            events = pygame.event.get()  # Store the list of events
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    direction = None
                    if event.key == pygame.K_UP:
                        direction = 'n'
                    elif event.key == pygame.K_DOWN:
                        direction = 's'
                    elif event.key == pygame.K_LEFT:
                        direction = 'w'
                    elif event.key == pygame.K_RIGHT:
                        direction = 'e'
                    if direction:
                        self.move_player(direction)
            self.ui.process_input(events) # pass processing of the events to the UI to handle mouse things
            # Rest of the game loop
            self.screen.fill((0, 0, 0))
            self.ui.display_room_info()
            half_window_width = self.window_width // 2
            self.map_visualizer.draw_map(self.screen, offset_x=half_window_width)
            self.ui.display_player_stats()
            pygame.display.flip()

    def spawn_enemies(self, count):
        for _ in range(count):  # Spawn count enemies
            while True:
                potential_start = random.choice(list(self.game_map.rooms.values()))
                if self.is_valid_spawn(potential_start):
                    enemy = Enemy(potential_start)
                    self.enemies.append(enemy)
                    break

    def is_valid_spawn(self, start_room):
        # Check distance from player and other enemies
        for other in [self.player] + self.enemies:
            if abs(start_room.x - other.x) <= 5 and abs(start_room.y - other.y) <= 5:
                return False
        return True
    
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

    def update_enemies_aggro(self):
        player_x, player_y = self.player.x, self.player.y
        for enemy in self.enemies:
            enemy.check_aggro(player_x, player_y)

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
    
    def move_enemies(self):
        for enemy in self.enemies:
            if self.player_move_count % enemy.speed == 0:
                if random.random() < 0.87:  # 87% chance to move
                    self.move_enemy(enemy)