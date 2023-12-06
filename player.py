from inventory import Inventory

class Player:
    def __init__(self, start_room):
        self.x, self.y = start_room.x, start_room.y
        self.current_room = start_room
        self.name = "PLAYER"
        self.atk = 0 # attack
        self.defn = 0 # defense
        self.int = 0 # intelligence
        self.wis = 0 # wisdom
        self.con = 0 # constitution
        self.cha = 0 # charisma
        self.exp = 0 # experience
        self.level = 0
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
            