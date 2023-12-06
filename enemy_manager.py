from enemy import Enemy
import random

class EnemyManager:
    def __init__(self, game_map, player, player_move_count):
        self.game_map = game_map
        self.player = player
        self.enemies = []
        self.spawn_enemies(10)
        self.player_move_count = player_move_count

    def check_chase_player(self):
        for enemy in self.enemies:
            if enemy.current_room == self.player.current_room:
                # switch the enemy's flag to following
                enemy.is_following_player = True

    def spawn_enemies(self, count):
        for num in range(count):  # Spawn count enemies
            while True:
                potential_start = random.choice(list(self.game_map.rooms.values()))
                if self.is_valid_spawn(potential_start):
                    enemy = Enemy(potential_start)
                    enemy.name = "Enemy " + str(num)
                    self.enemies.append(enemy)
                    break

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
                if random.random() < 0.87:  # 87% chance to move
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
            # Random movement logic if the enemy is not in the same room as the player
            if enemy.current_room != self.player.current_room:
                valid_directions = [dir for dir in ['n', 's', 'e', 'w'] if enemy.can_move(dir, self.game_map)]
                direction = random.choice(valid_directions) if valid_directions else None

                if direction:
                    enemy.current_room.enemy = None
                    new_room = self.game_map.rooms[(enemy.x, enemy.y)].connections[direction]
                    enemy.move_to_room(new_room)
                    new_room.enemy = enemy