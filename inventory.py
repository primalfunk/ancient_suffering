from sound_manager import SoundManager

class Inventory:
    def __init__(self, player, max_size=5):
        self.player = player
        self.sounds = SoundManager()
        self.items = []
        self.max_size = max_size
        self.full = False

    def add_item(self, item):
        if len(self.items) < self.max_size:
            self.items.append(item)
            self.sounds.play_sound('inventory', 0.75)
            # special effect item(s)
            if item == 'lantern':
                print(f"picked up lantern")
                self.player.visibility_radius = 4
            if item == 'map':
                print(f"picked up map")
                self.player.got_map = True
            return True
        else:
            self.full = True
            self.sounds.play_sound('gameover', 0.75)
            return False

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            self.sounds.play_sound('inventory', 0.75)
            if item == 'lantern':
                self.player.visibility_radius = 3
            return True
        else:
            if len(self.items) < self.max_size:
                self.full = False
            return False

    def has_item(self, item):
        return item in self.items

    def get_items(self):
        return self.items