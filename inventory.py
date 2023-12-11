from sound_manager import SoundManager

class Inventory:
    def __init__(self, player, game_manager, max_size=5):
        self.player = player
        self.game_manager = game_manager
        self.sounds = SoundManager()
        self.items = []
        self.max_size = max_size
        self.full = False

    def add_item(self, item):
        if len(self.items) < self.max_size:
            self.items.append(item)
            self.player.current_room.decorations.remove(item)
            self.sounds.play_sound('inventory', 0.75)
            light_source_changed = False
            if item in ('lantern', 'torch', 'table lamp'):
                self.player.visibility_radius = 4
                light_source_changed = True
            if item in ('flashlight', 'glowing rock'):
                self.player.visibility_radius = 5
                light_source_changed = True
            if item == 'map':
                for room in self.game_manager.game_map.rooms.values():
                    room.lit = 5
                light_source_changed = True
            if item == 'compass':
                self.game_manager.map_visualizer.draw_all_connections()
                light_source_changed = True
            if light_source_changed:
                self.game_manager.map_visualizer.update_light_levels(self.player.visibility_radius)
        else:
            self.full = True

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            self.player.current_room.decorations.append(item)
            self.sounds.play_sound('inventory', 0.75)
            if item in ('lantern', 'torch', 'flashlight', 'glowing rock', 'table lamp'):
                self.update_visibility_radius()
            return True
        else:
            if len(self.items) < self.max_size:
                self.full = False
            return False
    
    def update_visibility_radius(self):
        max_radius = 3
        if 'flashlight' or 'glowing rock' in self.items:
            max_radius = 5
        elif 'lantern' in self.items or 'torch' in self.items or 'table lamp' in self.items:
            max_radius = 4
        self.player.visibility_radius = max_radius

    def has_item(self, item):
        return item in self.items

    def get_items(self):
        return self.items