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
            self.defender = self.attacker.current_room.enemy
        else:
            self.defender = player
            self.attacker = self.defender.current_room.enemy
        self.player_damage = 0
        self.message_display.add_message("***** Entering Combat Mode *****", self.ORANGE)
        self.sounds.play_sound('notification', 0.5)
        self.message_display.add_message(f"* Combat has started between {self.attacker.name} and {self.defender.name}", self.ORANGE)
        self.attacker.in_combat = True
        self.defender.in_combat = True
        self.last_update_time = pygame.time.get_ticks()
        self.turn = 'attacker'
        self.is_player_attacker = is_attacker
        
    def attack(self, attacker, defender):
        self.combat_logger.debug(f"Starting attack: {attacker.name} attacking {defender.name}")
        luck_attempt = random.random()
        luck_chance = 0.10
        luck_success = luck_attempt <= luck_chance
        original_atk = attacker.atk
        original_defn = attacker.defn
        original_eva = attacker.eva
        original_int = attacker.int
        original_wis = attacker.wis
        if attacker == self.player:
            if luck_success:  # 10% chance of a luck boost
                luck_boost = 1.2  # 20% increase in stats
                attacker.atk = int(attacker.atk * luck_boost)
                attacker.defn = int(attacker.defn * luck_boost)
                attacker.eva = int(attacker.eva * luck_boost)
                attacker.int = int(attacker.int * luck_boost)
                attacker.wis = int(attacker.wis * luck_boost)
                self.combat_logger.debug(f"Luck boost applied. Original stats: ATK={original_atk}, DEFN={original_defn}, EVA={original_eva}; New stats: ATK={attacker.atk}, DEFN={attacker.defn}, EVA={attacker.eva}")
        critical_hit = False
        hit_chance = max(10, min(100, 70 + attacker.int - defender.eva))
        hit_attempt = random.randint(0, 100)
        hit = hit_attempt <= hit_chance
        damage = 0 # so it's picked up in case of a miss
        if hit:
            self.combat_logger.debug(f'Hit successful, checking dodge.')
            dodge_attempt = random.randint(0, 100)
            dodge_chance = 10  # 10% chance to dodge
            self.combat_logger.debug(f'dodge attempt {dodge_attempt} < dodge chance? {dodge_chance}: {dodge_attempt <= dodge_chance}')
            if dodge_attempt <= dodge_chance:
                dodge_message = f"* {defender.name} dodges the attack!"
                self.message_display.add_message(dodge_message, self.DARK_BLUE if attacker == self.player else self.LIGHT_RED)
                self.combat_logger.debug(f"{defender.name} dodged the attack. No damage dealt.")
                return 0, False  # No damage, no critical hit
            self.combat_logger.debug(f'Defender failed dodge attempt, calculating damage.')
            attack_variance = random.uniform(0.6, 2)
            defense_variance = random.uniform(0.6, 2)
            self.combat_logger.debug(f'attack variance and defense variance calculations: {attack_variance}, {defense_variance}')
            calculated_damage = (attacker.atk * attack_variance) - (defender.defn * defense_variance)
            self.combat_logger.debug(f'attacker atk {attacker.atk} * attack variance {attack_variance} - defender defn {defender.defn} * defense_variance {defense_variance}')
            self.combat_logger.debug(f"calculated damage is {calculated_damage}")
            damage = int(max(2, calculated_damage))
            self.combat_logger.debug(f'Ending damage calculation is max of 2 or calculated_damage {calculated_damage}')
            self.combat_logger.debug(f"Damage calculation is (atk {attacker.atk} * variance {attack_variance}) minus (defn {defender.defn} * variance {defense_variance}), Raw damage={calculated_damage}, Final damage={damage}")
            if self.is_player_attacker:
                base_critical_chance = 24
            else:
                base_critical_chance = 0
            critical_hit_chance = base_critical_chance + (attacker.wis - defender.wis) / 8
            critical_attempt = random.randint(0, 100)
            critical_hit = critical_attempt < critical_hit_chance
            self.combat_logger.debug(f"Critical hit check: Attempt={critical_attempt} Chance={critical_hit_chance}%, Result={'Yes' if critical_hit else 'No'}")
            if critical_hit:
                damage = int(damage*(2 + random.random()))
                self.combat_logger.debug(f"Critical hit! Final damage after multiplier: {damage}")
            if critical_hit:
                crit_message = f"* Critical hit by {attacker.name} doing {damage} damage!"
                self.message_display.add_message(crit_message, self.DARK_BLUE if attacker == self.player else self.LIGHT_RED)
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
        self.combat_logger.debug(f"End of attack: {attacker.name} did {damage} damage to {defender.name}. {defender.name}'s HP {defender.hp}")
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
        if self.attacker.hp > self.defender.hp:
            self.winner = self.attacker
            if self.is_player_attacker:
                self.sounds.play_sound('win', 0.75)
            else:
                self.sounds.play_sound('gameover', 0.75)
        elif self.defender.hp > self.attacker.hp:
            self.winner = self.defender
        else:
            self.winner = None
        winner_name = self.winner.name if self.winner else "None"
        self.sounds.play_sound('win', 0.75)
        self.message_display.add_message(f"* Combat has ended. Winner: {winner_name}", self.ORANGE)
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
        elif self.winner != self.player and self.player.hp <= 0:
            self.message_display.add_message(f"* {self.player.name} defeated, game over. Press (q) to quit or (r) to restart.", (255, 120, 120))
            self.disable_inputs_except_quit_restart()
        self.is_over = True
        self.message_display.add_message(f"***** Exited Combat Mode *****", self.ORANGE)
        self.resume_regular_music()
        return self.is_over
            
    def disable_inputs_except_quit_restart(self):
        pass

    def init_music(self, volume):
        pygame.mixer.music.load('music/battlemusic.mp3')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(volume)

    def resume_regular_music(self):
        pygame.time.wait(1000)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.load('music/bgmusic.mp3')
        pygame.mixer.music.play(-1)
        