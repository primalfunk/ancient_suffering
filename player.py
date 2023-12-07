from inventory import Inventory

class Player:
    def __init__(self, start_room):
        self.x, self.y = start_room.x, start_room.y
        self.current_room = start_room
        self.in_combat = False
        self.name = "PLAYER"
        self.atk = 10 # attack
        self.defn = 10 # defense
        self.int = 1 # intelligence
        self.wis = 1 # wisdom
        self.con = 1 # constitution
        self.eva = 1 # evasion
        self.exp = 0 # experience
        self.level = 1
        self.hp = 50
        self.mp = 10
        self.inventory = Inventory()
        self.equipped_weapon = None
        self.equipped_armor = None

    def move_to_room(self, new_room):
        self.x, self.y = new_room.x, new_room.y
        self.current_room = new_room

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

    def unequip_item(self, item, category):
        if category == "W":
            self.equipped_weapon = None
            self.atk -= 30 # or whatever
        elif category == 'A':
            self.equipped_armor = None
            self.defn -= 30 # or whatever
        self.current_room.decorations.append(item)

    def check_level_up(self):
        # Example: Increase level for every 25 exp
        if self.exp >= 25:
            self.level += 1
            self.exp -= 25
            return True  # if it happened, return True
        return False