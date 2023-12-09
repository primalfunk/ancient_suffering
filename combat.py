import logging
import pygame
import random
from sound_manager import SoundManager

class Combat:
    LIGHT_BLUE = (173, 216, 230)
    DARK_BLUE = (0, 0, 139)
    LIGHT_RED = (255, 182, 193)
    BRIGHT_RED = (255, 0, 0)
    ORANGE = (255, 165, 0)

    def __init__(self, player, is_attacker, enemy_manager, message_display):
        self.sounds = SoundManager()
        self.combat_logger = logging.getLogger('combat')
        self.player = player
        self.is_player_attacker = is_attacker
        self.enemy_manager = enemy_manager
        self.message_display = message_display
        self.winner = None
        self.is_over = False
        if is_attacker:
            self.attacker = player
            self.defender = self.attacker.current_room.enemy
        else:
            self.defender = player
            self.attacker = self.defender.current_room.enemy
        self.message_display.add_message("***** Entering Combat Mode *****", self.ORANGE)
        self.sounds.play_sound('notification', 0.5)
        self.message_display.add_message(f"* Combat has started between {self.attacker.name} and {self.defender.name}")
        
        self.attacker.in_combat = True
        self.defender.in_combat = True
        self.last_update_time = pygame.time.get_ticks()
        self.turn = 'attacker'

    def attack(self, attacker, defender):
        dodge_chance = 10  # 10% chance to dodge
        if random.randint(0, 100) < dodge_chance:
            miss_message = f"* {defender.name} dodges the attack!"
            self.message_display.add_message(miss_message, self.DARK_BLUE if attacker == self.player else self.LIGHT_RED)
            return 0, False  # No damage, no critical hit
        # Luck boost
        if random.random() < 0.1:  # 10% chance of a luck boost
            luck_boost = 1.3  # 30% increase in stats
            attacker.atk = round(attacker.atk * luck_boost, 0)
            attacker.defn = round(attacker.defn * luck_boost, 0)
            attacker.eva = round(attacker.eva * luck_boost, 0)
        # Critical hit calculation
        critical_hit = False
        hit_chance = max(5, min(100, 50 + (attacker.int - defender.eva) / 4))
        hit = random.randint(0, 100) < hit_chance
        damage = 0
        if hit:
            attack_variance = random.uniform(0.6, 2)
            defense_variance = random.uniform(0.6, 2) 
            damage = round(max(2, (attacker.atk * attack_variance) - (defender.defn * defense_variance)), 0)
            # Enhanced critical hit mechanics
            base_critical_chance = 33  # Increased base critical chance
            critical_hit_chance = base_critical_chance + (attacker.wis - defender.wis) / 4
            critical_hit = random.randint(0, 100) < critical_hit_chance
            if critical_hit:
                damage *= 3
        # Apply damage and display messages
        defender.hp -= damage
        self.sounds.play_sound('round', 0.6)
        if critical_hit:
            crit_message = f"* Critical hit by {attacker.name}!"
            self.message_display.add_message(crit_message, self.DARK_BLUE if attacker == self.player else self.LIGHT_RED)
        else:
            attack_message = f"* {attacker.name} hits {defender.name} for {damage} damage."
            self.message_display.add_message(attack_message, self.DARK_BLUE if attacker == self.player else self.LIGHT_RED)

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > 1500:
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
        self.message_display.add_message(f"* Combat has ended. Winner: {winner_name}")

    def combat_over(self):
        # Handling the combat outcome
        if self.winner == self.player:
            # Player wins the combat
            pygame.mixer.music.stop()
            self.sounds.play_sound('win', 0.75)
            defeated_enemy = self.defender if self.is_player_attacker else self.attacker
            self.message_display.add_message(f"* {self.player.name} has defeated {defeated_enemy.name}.")
            # Remove defeated enemy from the game
            self.enemy_manager.enemies.remove(defeated_enemy)
            self.player.current_room.enemies.remove(defeated_enemy)
            # Convert defeated enemy to a decoration
            corpse_item = f"corpse ({defeated_enemy.name})"
            self.player.current_room.decorations.append(corpse_item)
            # Award experience to the player
            self.player.exp += defeated_enemy.exp
            self.message_display.add_message(f"* {self.player.name} gains {defeated_enemy.exp} experience.")
            if self.player.check_level_up():
                stat_increases = self.player.level_up()
                for stat, increase in stat_increases.items():
                    self.message_display.add_message(f"{self.player.name}'s {stat} increased by {increase}.")
                self.sounds.play_sound('arcane', 0.5)
                self.message_display.add_message(f"* {self.player.name} has leveled up! New level is {self.player.level}")
        elif self.winner != self.player and self.player.hp <= 0:
            # Player is defeated
            self.sounds.play_sound('gameover', 0.75)
            self.message_display.add_message(f"* {self.player.name} defeated, game over. Press (q) to quit or (r) to restart.")
            self.disable_inputs_except_quit_restart()
        self.is_over = True
        pygame.mixer.music.stop()
        self.message_display.add_message(f"***** Exited Combat Mode *****", self.ORANGE)
        self.resume_regular_music()
        return self.is_over
        
    def resolve_combat(self):
        self.attacker.in_combat = False
        self.defender.in_combat = False
        self.determine_winner()
        self.combat_over()
    
    def disable_inputs_except_quit_restart(self):
        pass

    def init_music(self, volume):
        pygame.mixer.music.load('battlemusic.mp3')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(volume)

    def resume_regular_music(self):
        pygame.time.wait(1000)
        pygame.mixer.music.set_volume(0.3)  # Adjust volume as needed
        pygame.mixer.music.load('bgmusic.mp3')  # Path to your regular music track
        pygame.mixer.music.play(-1)  # Loop the music
        