import logging
import pygame
import random

# Configure logging
logging.basicConfig(filename='boot.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Combat:
    def __init__(self, player, is_attacker, enemy_manager, message_display):
        self.player = player
        self.is_player_attacker = is_attacker
        self.enemy_manager = enemy_manager
        self.message_display = message_display
        self.winner = None
        self.is_over = False
        # sort out which entities are attacker and defender
        if is_attacker:
            self.attacker = player
            self.defender = self.attacker.current_room.enemy
        else:
            self.defender = player
            self.attacker = self.defender.current_room.enemy
        self.message_display.add_message(f"Combat has started between {self.attacker.name} and {self.defender.name}")
        
        self.attacker.in_combat = True
        self.defender.in_combat = True
        self.last_update_time = pygame.time.get_ticks()
        
        self.turn = 'attacker'

    def attack(self, attacker, defender):
        if random.randint(0, 100) >= defender.eva:
            damage = max(attacker.atk - defender.defn, 0)
            defender.hp -= damage
            self.message_display.add_message(f"{attacker.name} hits {defender.name} for {damage} damage.")

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > 1000:
            if self.turn == 'attacker':
                self.attack(self.attacker, self.defender)
                self.turn = 'defender'
            elif self.turn == 'defender':
                self.attack(self.defender, self.attacker)
                self.turn = 'attacker'
            self.check_combat_end()
            self.last_update_time = current_time

    def check_combat_end(self):
        if self.attacker.hp <= 0 or self.defender.hp <= 0:
            self.resolve_combat()

    def determine_winner(self):
        if self.attacker.hp > self.defender.hp:
            self.winner = self.attacker
        elif self.defender.hp > self.attacker.hp:
            self.winner = self.defender
        else:
            self.winner = None
        winner_name = self.winner.name if self.winner else "None"
        self.message_display.add_message(f"Combat has ended. Winner: {winner_name}")

    def combat_over(self):
        # Handling the combat outcome
        if self.winner == self.player:
            # Player wins the combat
            defeated_enemy = self.defender if self.is_player_attacker else self.attacker
            self.message_display.add_message(f"{self.player.name} as defeated {defeated_enemy}.")
            # Remove defeated enemy from the game
            self.enemy_manager.enemies.remove(defeated_enemy)
            self.player.current_room.enemies.remove(defeated_enemy)
            # Convert defeated enemy to a decoration
            corpse_item = f"corpse ({defeated_enemy.name})"
            self.player.current_room.decorations.append(corpse_item)
            # Award experience to the player
            self.player.exp += defeated_enemy.exp
            self.message_display.add_message(f"{self.player.name} gains {defeated_enemy.exp} experience.")
            if self.player.check_level_up():
                self.message_display.add_message(f"{self.player.name} has leveled up! New level is {self.player.level}")
        elif self.winner != self.player and self.player.hp <= 0:
            # Player is defeated
            self.message_display.add_message(f"{self.player.name} defeated, game over. Press (q) to quit or (r) to restart.")
            self.disable_inputs_except_quit_restart()
        self.is_over = True
        return self.is_over
        
    def resolve_combat(self):
        self.attacker.in_combat = False
        self.defender.in_combat = False
        self.determine_winner()
        self.combat_over()
    
    def disable_inputs_except_quit_restart(self):
        pass