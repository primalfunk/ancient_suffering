from inventory import Inventory
import random
from sound_manager import SoundManager

class Player:
    def __init__(self, start_room):
        self.sounds = SoundManager()
        self.x, self.y = start_room.x, start_room.y
        self.current_room = start_room
        self.in_combat = False
        self.name = "PLAYER"
        self.atk = 10 # attack
        self.defn = 10 # defense
        self.int = 0 # intelligence
        self.wis = 0 # wisdom
        self.con = 0 # constitution
        self.eva = 0 # evasion
        self.exp = 0 # experience
        self.level = 1
        self.max_hp = 50
        self.hp = 50
        self.max_mp = 50
        self.mp = 50
        self.inventory = Inventory(self)
        self.equipped_weapon = None
        self.equipped_armor = None
        self.got_map = False
        self.visibility_radius = 3
    
    def move_to_room(self, new_room):
        self.x, self.y = new_room.x, new_room.y
        self.current_room = new_room
        if self.hp < self.max_hp: # regen feature
            self.hp += 1

    def can_move(self, direction, game_map):
        current_room = game_map.rooms[(self.x, self.y)]
        if direction in current_room.connections and current_room.connections[direction] is not None:
            return True
        return False
    
    def equip_item(self, item, category):
        if category == 'W':
            self.equipped_weapon = item
            self.atk += 30 # or whatever
        elif category == 'A':
            self.equipped_armor = item
            self.defn += 30 # or whatever
        self.current_room.decorations.remove(item)
        self.sounds.play_sound('inventory', 0.75)

    def unequip_item(self, item, category):
        if category == "W":
            self.equipped_weapon = None
            self.atk -= 30 # or whatever
        elif category == 'A':
            self.equipped_armor = None
            self.defn -= 30 # or whatever
        self.current_room.decorations.append(item)
        self.sounds.play_sound('inventory', 0.75)

    def check_level_up(self):
        level_up_threshold = self.calculate_level_up_threshold()
        if self.exp >= level_up_threshold:
            return True
        return False
    
    def calculate_level_up_threshold(self):
        return 25 * 2 ** (self.level - 1)

    def level_up(self):
        self.level += 1
        stat_increases = {
        'atk': random.randint(2, 5) + 2,
        'defn': random.randint(2, 5) + 2,
        'int': random.randint(1, 3) + self.level // 5,
        'wis': random.randint(1, 3) + self.level // 5,
        'con': random.randint(1, 3),
        'eva': random.randint(1, 3),
        'max_hp': self.con * 2 + self.level,
        'max_mp': random.randint(1, 3) + self.level // 2}

        for stat, increase in stat_increases.items():
            setattr(self, stat, getattr(self, stat) + increase)

        self.hp = self.max_hp
        self.mp = self.max_mp

        self.sounds.play_sound('win', 0.5)
        return stat_increases