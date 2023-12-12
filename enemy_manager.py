from enemy import Enemy
import json
import random

class EnemyManager:
    def __init__(self, game_map, player, player_move_count):
        self.name = ""
        self.game_map = game_map
        self.player = player
        self.spawn_count = self.game_map.size // 3
        self.enemies = []
        self.spawn_enemies(self.spawn_count, self.player.level)
        self.player_move_count = player_move_count

    def load_words(self):
        with open('words.json') as file:
            return json.load(file)

    def check_chase_player(self):
        for enemy in self.enemies:
            if enemy.current_room == self.player.current_room:
                enemy.is_following_player = True

    def spawn_enemies(self, count, player_level):
        for num in range(count):
            potential_start, level_indicator = None, None
            for _ in range(100):  # Limit attempts to avoid infinite loop
                potential_start = random.choice(list(self.game_map.rooms.values()))
                if self.is_valid_spawn(potential_start):
                    level_indicator = random.randint(0, 100)
                    break
            if not potential_start or level_indicator is None:
                continue  # Skip if no valid location found
            enemy_level = self.determine_enemy_level(level_indicator, player_level)
            enemy = self.create_enemy(potential_start, enemy_level, num)
            self.enemies.append(enemy)
            print(f"Enemy generated: {enemy.get_stats()}")

    def determine_enemy_level(self, level_indicator, player_level):
        if level_indicator < 6:
            return player_level + 3
        elif level_indicator < 17:
            return player_level + 2
        elif level_indicator < 33:
            return player_level + 1
        else:
            return player_level

    def create_enemy(self, start_position, level, identifier):
        words = self.load_words()
        adjective = random.choice(words['adjectives']['enemies']).title()
        noun = random.choice(words['enemies']).title()
        enemy = Enemy(start_position, level)
        enemy.id = identifier
        enemy.name = f"{adjective} {noun} ( level {level} )"
        return enemy
      
    def is_valid_spawn(self, start_room):
        for other in [self.player] + self.enemies:
            if abs(start_room.x - other.x) <= 3 and abs(start_room.y - other.y) <= 3:
                return False
        return True
    
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
  
    def move_enemies(self):
        self.update_enemies_aggro()
        for enemy in self.enemies:
            if self.player_move_count % enemy.speed == 0:
                if random.random() < 0.87:
                    self.move_enemy(enemy)

    def move_enemy(self, enemy):
        if enemy.is_following_player:
            enemy.current_room == self.player.current_room
        elif enemy.aggro:
            path = enemy.find_path_to_player(self.player, self.game_map)
            next_room = enemy.next_move_on_path(path)
            if next_room:
                enemy.current_room.enemy = None
                enemy.move_to_room(next_room)
                next_room.enemy = enemy
        else:
            if enemy.current_room != self.player.current_room:
                valid_directions = [dir for dir in ['n', 's', 'e', 'w'] if enemy.can_move(dir, self.game_map)]
                direction = random.choice(valid_directions) if valid_directions else None

                if direction:
                    enemy.current_room.enemy = None
                    new_room = self.game_map.rooms[(enemy.x, enemy.y)].connections[direction]
                    enemy.move_to_room(new_room)
                    new_room.enemy = enemy