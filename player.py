from inventory import Inventory
import random
from sound_manager import SoundManager

class Player:
    def __init__(self, start_room, game_manager, level=1):
        self.game_manager = game_manager
        self.sounds = SoundManager()
        self.x, self.y = start_room.x, start_room.y
        self.current_room = start_room
        self.in_combat = False
        self.got_relic = False
        self.name = "PLAYER"
        self.level = max(level, 1)
        self.initialize_stats_based_on_level() # lvl one for player
        self.inventory = Inventory(self, game_manager)
        self.equipped_weapon = None
        self.equipped_armor = None
        self.has_map = False
        self.has_compass = False
        self.visibility_radius_changed = False
        self.visibility_radius = 3
        self.calculate_exp_requirements()
        
    def initialize_stats_based_on_level(self):
        self.atk = 10
        self.defn = 10
        self.int = 10
        self.wis = 10
        self.con = 10
        self.eva = 10
        self.exp = 0
        self.hp = 50
        self.mp = 10
        self.max_hp = 50
        self.max_mp = 10
        self.hp = self.max_hp
        self.mp = self.max_mp
    
    def move_to_room(self, new_room):
        self.x, self.y = new_room.x, new_room.y
        self.current_room = new_room
        if self.hp < self.max_hp:
            self.hp += 1

    def can_move(self, direction, game_map):
        current_room = game_map.rooms[(self.x, self.y)]
        if direction in current_room.connections and current_room.connections[direction] is not None and self.hp > 0: # can only move if not dead!
            return True
        return False
    
    def equip_item(self, item, category):
        # expansion here and in the data to take a unique value for a piece of equipment
        if category == 'W':
            self.equipped_weapon = item
            self.atk += 10 # or whatever
        elif category == 'A':
            self.equipped_armor = item
            self.defn += 10 # or whatever
        self.current_room.decorations.remove(item)
        self.sounds.play_sound('inventory', 0.75)

    def unequip_item(self, item, category):
        if category == "W":
            self.equipped_weapon = None
            self.atk -= 10 # or whatever
        elif category == 'A':
            self.equipped_armor = None
            self.defn -= 10 # or whatever
        self.current_room.decorations.append(item)
        self.sounds.play_sound('inventory', 0.75)

    def calculate_stat_increase(self, current_stat, initial_value, max_value, current_level):
        growth_rate = (max_value - initial_value) / 99  # Linear growth rate
        expected_value = initial_value + growth_rate * (current_level - 1)
        increase = expected_value - current_stat + random.randint(1, 3)
        return int(max(1, min(max_value - current_stat, increase)))

    def level_up(self):
        self.level += 1
        stat_increases = {
            'hp': self.calculate_stat_increase(self.hp, 50, 999, self.level),
            'mp': self.calculate_stat_increase(self.mp, 10, 999, self.level),
            'atk': self.calculate_stat_increase(self.atk, 10, 255, self.level),
            'defn': self.calculate_stat_increase(self.defn, 10, 255, self.level),
            'int': self.calculate_stat_increase(self.int, 10, 255, self.level),
            'wis': self.calculate_stat_increase(self.wis, 10, 255, self.level),
            'con': self.calculate_stat_increase(self.con, 10, 255, self.level),
            'eva': self.calculate_stat_increase(self.eva, 10, 255, self.level)
        }
        for stat, increase in stat_increases.items():
            setattr(self, stat, getattr(self, stat) + increase)
        return stat_increases
    
    def calculate_exp_requirements(self):
        base_exp = 50
        target_exp_at_100 = 1000000
        growth_factor = (target_exp_at_100 / base_exp) ** (1 / 98)
        cumulative_exp = 0  # Initialize cumulative experience
        self.exp_requirements = [cumulative_exp]
        for lvl in range(1, self.level + 1):
            next_exp = base_exp * (growth_factor ** (lvl - 1))
            cumulative_exp += int(next_exp)  # Accumulate the experience required
            self.exp_requirements.append(cumulative_exp)

    def check_level_up(self):
        self.calculate_exp_requirements()
        if self.level < 100 and self.exp >= self.exp_requirements[self.level]:
            return True
        return False