import logging
import logging_config
import pygame
import random
from sound_manager import SoundManager

class Combat:
    logging_config.setup_logging()
    LIGHT_BLUE = (173, 216, 230)
    DARK_BLUE = (50, 50, 230)
    LIGHT_RED = (230, 50, 50)
    BRIGHT_RED = (255, 0, 0)
    ORANGE = (255, 165, 0)

    def __init__(self, player, is_attacker, enemy_manager, message_display):
        self.sounds = SoundManager()
        self.round_count = 0
        self.combat_logger = logging.getLogger('combat')
        self.player = player
        self.enemy_manager = enemy_manager
        self.message_display = message_display
        self.winner = None
        self.is_over = False
        if is_attacker:
            self.attacker = player
            self.defender = self.attacker.current_room.enemies[0]
        else:
            self.defender = player
            self.attacker = self.defender.current_room.enemies[0]
        self.player_damage = 0
        self.message_display.add_message("***** Entering Combat Mode *****", self.ORANGE)
        self.sounds.play_sound('notification', 0.5)
        self.message_display.add_message(f"* Combat has started between {self.attacker.name} and {self.defender.name}", self.ORANGE)
        self.attacker.in_combat = True
        self.defender.in_combat = True
        self.last_update_time = pygame.time.get_ticks()
        self.turn = 'attacker'
        self.is_player_attacker = is_attacker
        self.player_won = False
        
    def attack(self, attacker, defender):
        self.combat_logger.debug(f"Starting attack: {attacker.name} attacking {defender.name}")
        luck_attempt = random.random()
        luck_chance = 0.20
        luck_success = luck_attempt <= luck_chance
        original_atk = attacker.atk
        original_defn = attacker.defn
        original_eva = attacker.eva
        original_int = attacker.int
        original_wis = attacker.wis
        if attacker == self.player:
            if luck_success:  # 20% chance of a luck boost
                luck_boost = 1.33  # 33% increase in stats
                attacker.atk = int(attacker.atk * luck_boost)
                attacker.defn = int(attacker.defn * luck_boost)
                attacker.eva = int(attacker.eva * luck_boost)
                attacker.int = int(attacker.int * luck_boost)
                attacker.wis = int(attacker.wis * luck_boost)
                self.combat_logger.debug(f"Luck boost applied. Original stats: ATK={original_atk}, DEFN={original_defn}, EVA={original_eva}; New stats: ATK={attacker.atk}, DEFN={attacker.defn}, EVA={attacker.eva}")
        critical_hit = False
        if self.is_player_attacker:
            hit_chance = max(10, min(100, 70 + attacker.int - int(2 * defender.eva / 3)))
        hit_attempt = random.randint(0, 100)
        hit = hit_attempt <= hit_chance
        damage = 0 # so it's picked up in case of a miss
        if hit:
            self.combat_logger.debug(f'Hit successful, checking dodge.')
            dodge_attempt = random.randint(0, 100)
            dodge_chance = 10
            if dodge_attempt <= dodge_chance:
                dodge_message = f"* {defender.name} dodges the attack!"
                self.message_display.add_message(dodge_message, self.DARK_BLUE if attacker == self.player else self.LIGHT_RED)
                return 0, False  # No damage, no critical hit
            attack_variance = random.uniform(0.8, 1.01)
            defense_variance = random.uniform(0.8, 1.01)
            calculated_damage = int((attacker.atk * attack_variance) - ((defender.defn * defense_variance) * 2 / 3))
            damage = int(max(0, calculated_damage)) # damage
            base_critical_chance = 10
            critical_hit_chance = base_critical_chance + (attacker.wis - defender.wis) / 8
            critical_attempt = random.randint(0, 100)
            critical_hit = critical_attempt < critical_hit_chance
            if critical_hit and self.is_player_attacker:
                damage = int(damage*(2 + random.random()))
                crit_message = f"* Critical hit by {attacker.name} doing {damage} damage!"
                self.message_display.add_message(crit_message, self.DARK_BLUE if attacker == self.player else self.LIGHT_RED)
            else:
                actual_damage = round(damage, 0)
                print(f"Actual damage: {actual_damage}")
                if actual_damage == 0:
                    attack_message = f"* {attacker.name} hits {defender.name}, but the attack is harmless."
                else:
                    attack_message = f"* {attacker.name} hits {defender.name} for {damage} damage."
                
                self.message_display.add_message(attack_message, self.DARK_BLUE if attacker == self.player else self.LIGHT_RED)
            defender.hp -= int(damage)
            self.sounds.play_sound('round', 0.6)
            if self.turn == 'attacker' and self.is_player_attacker:
                self.player_damage += damage
        else:
            miss_message = f"* {attacker.name} misses {defender.name}"
            self.message_display.add_message(miss_message, self.DARK_BLUE if attacker == self.player else self.LIGHT_RED)
        self.round_count += 1
        attacker.atk = original_atk
        attacker.defn = original_defn
        attacker.eva = original_eva
        attacker.int = original_int
        attacker.wis = original_wis

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

    def resolve_combat(self):
        self.attacker.in_combat = False
        self.defender.in_combat = False
        self.determine_winner()
        self.combat_over()

    def determine_winner(self):
        winner_banner = ""
        if self.player.hp > 0:
            self.sounds.play_sound('win', 0.75)
            self.winner = self.player
            self.player_won = True
            winner_banner = "has won!"
        else:
            self.player_won = False
            self.sounds.play_sound('gameover', 0.75)
            winner_banner = "has lost!"
        self.message_display.add_message(f"* Combat has ended. {self.player.name} {winner_banner}", self.ORANGE)
        self.message_display.add_message(f"* The battle lasted {self.round_count // 2} rounds; {self.player.name} dealt {self.player_damage} damage.")

    def combat_over(self):
        pygame.mixer.music.stop()
        if self.winner == self.player:
            defeated_enemy = self.defender if self.is_player_attacker else self.attacker
            self.message_display.add_message(f"* {self.player.name} has defeated {defeated_enemy.name}.")
            if defeated_enemy in self.enemy_manager.enemies:
                self.enemy_manager.enemies.remove(defeated_enemy)
            if defeated_enemy in self.player.current_room.enemies:
                self.player.current_room.enemies.remove(defeated_enemy)
            corpse_item = f"corpse ({defeated_enemy.name})"
            self.player.current_room.decorations.append(corpse_item)
            self.player.exp += defeated_enemy.exp
            self.message_display.add_message(f"* {self.player.name} gains {defeated_enemy.exp} experience.")
            
            if self.player.check_level_up():
                stat_increases = self.player.level_up()
                for stat, increase in stat_increases.items():
                    self.message_display.add_message(f"# {self.player.name}'s {stat} increased by {increase}.")
                self.message_display.add_message(f"# Congratulations, {self.player.name} has leveled up! Your level is {self.player.level}", (20, 240, 20))
                self.sounds.play_sound('arcane', 0.75)
        elif self.winner != self.player or self.player.hp <= 0:
            self.message_display.add_message(f"* {self.player.name} defeated, game over. Press (q) to quit or (r) to restart.", (255, 120, 120))
        self.is_over = True
        self.message_display.add_message(f"***** Exited Combat Mode *****", self.ORANGE)
        self.resume_regular_music()
        return self.is_over

    def init_music(self, volume):
        pygame.mixer.music.load('music/battlemusic.mp3')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(volume)

    def resume_regular_music(self):
        pygame.time.wait(1000)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.load('music/bgmusic.mp3')
        pygame.mixer.music.play(-1)
        