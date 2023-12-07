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

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > 1000:
            if self.turn == 'attacker':
                if random.randint(0, 100) >= self.defender.eva:
                    damage = max(self.attacker.atk - self.defender.defn, 0)
                    self.defender.hp -= damage
                    self.message_display.add_message(f"{self.attacker.name} hits {self.defender.name} for {damage} damage.")
                self.turn = 'defender'
            elif self.turn == 'defender':
                if random.randint(0, 100) >= self.attacker.eva:
                    damage = max(self.defender.atk - self.attacker.defn, 0)
                    self.attacker.hp -= damage
                    self.message_display.add_message(f"{self.defender.name} hits {self.attacker.name} for {damage} damage.")
                self.turn = 'attacker'
            if self.attacker.hp <= 0 or self.defender.hp <= 0:
                self.resolve_combat()
            self.last_update_time = current_time

    def resolve_combat(self):
        self.attacker.in_combat = False
        self.defender.in_combat = False
        self.determine_winner()
        self.combat_over()

    def determine_winner(self):
        if self.attacker.hp > self.defender.hp:
            self.winner = "player" if self.is_player_attacker else "enemy"
        elif self.defender.hp > self.attacker.hp:
            self.winner = "enemy" if self.is_player_attacker else "player"
        else:
            self.winner = None
        self.message_display.add_message(f"Combat has ended. Winner: {self.winner}")

    def combat_over(self):
        if self.player.hp > 0:
            self.player.check_level_up()    
            self.message_display.add_message(f"Congratulations, {self.defender.name} gained a level! You are now level {self.defender.level}")
        if self.winner == "player" and self.is_player_attacker:
            if self.defender in self.enemy_manager.enemies:
                self.enemy_manager.enemies.remove(self.defender) # remove defeated enemy from enemy_manager list (won't be moved anymore)
            if self.defender in self.attacker.current_room.enemies:
                self.attacker.current_room.enemies.remove(self.defender) # remove defeated enemy from the room
            self.attacker.exp += self.defender.exp
            self.message_display.add_message(f"{self.attacker.name} gains {self.defender.exp} experience.")
        elif self.winner == "player" and not self.is_player_attacker:
            self.enemy_manager.enemies.remove(self.attacker)
            self.defender.current_room.enemies.remove(self.attacker)
            self.defender.exp += self.attacker.exp
            self.message_display.add_message(f"{self.defender.name} gains {self.attacker.exp} experience.")

        elif self.winner == "enemy":
            # Player defeat logic
            self.message_display.add_message(f"{self.attacker.name} defeated, game over. Press (q) to quit or (r) to restart.")
            self.disable_inputs_except_quit_restart()
        
        self.is_over = True
        return self.is_over
        
    
    def disable_inputs_except_quit_restart(self):
        pass