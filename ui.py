from combat import Combat
import json
import logging
import pygame
from message_display import MessageDisplay
import random
from room_display import RoomDisplay
from sound_manager import SoundManager

class UI: 
    def __init__(self, screen, player, window_width, window_height, game_manager):
        self.screen = screen
        self.sounds = SoundManager()
        self.n_button_rect = None
        self.s_button_rect = None
        self.w_button_rect = None
        self.e_button_rect = None
        self.middle_button_label = None
        self.middle_button_rect = None
        self.player = player
        self.inventory_item_rects = []
        self.window_width = window_width
        self.window_height = window_height
        self.custom_font = pygame.font.Font('fonts/messages.ttf', 22)
        self.last_room_id = None
        self.to_render = []
        self.game_manager = game_manager
        self.room_display = RoomDisplay(screen, player, self.custom_font, (window_width, window_height))
        self.message_display_height = window_height // 2
        self.message_display_y = 2 * self.window_height // 3 - self.message_display_height
        self.message_display_bottom = self.message_display_y + self.message_display_height
        self.message_display = MessageDisplay(    
            x=0, 
            y=self.message_display_y, 
            width=self.window_width // 2, 
            height=self.message_display_height,
            font=self.custom_font
        )
        self.item_category_map = self.parse_item_categories()
        self.current_state = None
        self.show_intro_message()

    def get_random_color(self):
            r = random.randint(0, 120)
            g = random.randint(0, 120)
            b = random.randint(0, 120)
            random_color = (r, g, b)
            return random_color

    def show_intro_message(self):
        self.message_display.add_message('You have been transported into the Chaos dimension by the Lords of Chaos!', self.get_random_color())
        self.message_display.add_message("")
        self.message_display.add_message('In this realm, everything is familiar, but nothing makes sense. Your only hope of escape is to find the artifact of your reality - wherever it may be hidden in this twisted land.', self.get_random_color())
        self.message_display.add_message('')
        self.message_display.add_message("")
        self.message_display.add_message("Move between areas with the keyboard direction arrows, or clicking the buttons below. You can restart or quit at any time by pressing 'q' or 'r' on your keyboard.", self.get_random_color())
        self.message_display.add_message("")
        self.message_display.add_message("Go forth, and good luck - may the Lords of Chaos have mercy on you.", (0, 0, 0))
        self.message_display.add_message("")
        self.message_display.add_message("--------The Chaos Realm---------")

    def draw_hp_bar(self):
        surface_height = self.window_height * 3 // 4 - self.message_display_bottom
        surface_width = self.window_width // 2
        surface = pygame.Surface((surface_width, surface_height))
        reduced_font = pygame.font.Font('fonts/messages.ttf', 18)

        def draw_bar(hp, max_hp, y, color, label):
            text = reduced_font.render(label, True, (255, 255, 255))
            text_rect = text.get_rect()
            text_rect.topleft = (5, y - 5)
            surface.blit(text, text_rect)
            hp_ratio = hp / max_hp
            max_hp_bar_width = surface_width - text_rect.width - 15
            hp_bar_width = int(max_hp_bar_width * hp_ratio)
            hp_bar_height = 5
            hp_bar_rect = pygame.Rect(text_rect.topright[0] + 5, y, hp_bar_width, hp_bar_height)
            pygame.draw.rect(surface, color, hp_bar_rect)

        draw_bar(self.player.hp, self.player.max_hp, 20, (50, 230, 50), 'Player HP')
        y_offset = 40
        for enemy in self.player.current_room.enemies:
            draw_bar(enemy.hp, enemy.max_hp, y_offset, (230, 50, 50), 'Enemy HP')
            y_offset += 20
        self.screen.blit(surface, (0, self.message_display_bottom))

    def parse_item_categories(self):
        category_map = {}
        with open('words.json', 'r') as file:
            data = json.load(file)
            for category, items in data["objects"].items():
                for item in items:
                    if category == "tools":
                        category_map[item] = 'T'
                    elif category == "weapons":
                        category_map[item] = 'W'
                    elif category == "armor":
                        category_map[item] = 'A'
                    elif category == "artifacts":
                        category_map[item] = 'K'
        return category_map

    def update_ui(self):
        lower_ui_surface = pygame.Surface((self.window_width // 2, self.window_height // 4))
        lower_ui_surface.fill((0, 0, 0))
        padding = 10
        self.render_middle_button_and_inventory_frame(lower_ui_surface, padding)
        self.render_direction_buttons(lower_ui_surface, padding)
        border_color = (144, 238, 144)
        pygame.draw.rect(lower_ui_surface, border_color, lower_ui_surface.get_rect(), 2)
        self.screen.blit(lower_ui_surface, (0, self.window_height * 3 // 4))
        self.render_player_stats(self.screen)
        self.message_display.render(self.screen)
        self.draw_hp_bar()

    def render_player_stats(self, screen):
        stats_height = self.window_height // 8
        custom_font = pygame.font.Font('fonts/messages.ttf', 18)
        stats_surface = pygame.Surface((self.window_width // 2, stats_height))
        stats_surface.fill((50, 50, 50))
        first_column_attributes = ['name', 'level', 'hp', 'mp', 'exp']
        second_column_attributes = ['atk', 'defn', 'int', 'wis', 'con', 'eva']
        third_column_attributes = ['region', 'name', 'x', 'perc_lit']
        quarter_width = (self.window_width // 2) // 4
        offsets = [quarter_width * (i + 1) - (quarter_width // 2) for i in range(4)]
        text_color = (144, 236, 144)  # Consistent text color
        
        def draw_column_border(x_offset, color):
            border_rect = pygame.Rect(x_offset - quarter_width // 2, 0, quarter_width, stats_height)
            pygame.draw.rect(stats_surface, color, border_rect, 2)
        column_colors = [(135, 206, 235), (152, 251, 152), (230, 230, 250), (255, 253, 208)]
        for offset, color in zip(offsets, column_colors):
            draw_column_border(offset, color)

        def render_text_for_column(attributes, offset, get_attr_function):
            y_offset = self.window_height * 0.02  # 2% of window height
            for attr in attributes:
                text = get_attr_function(attr)
                text_surface = custom_font.render(text, True, text_color)
                stats_surface.blit(text_surface, (offset - (text_surface.get_width() // 2), y_offset))
                y_offset += 20

        render_text_for_column(first_column_attributes, offsets[0], lambda attr: f"{attr.title()}: {getattr(self.player, attr)}")
        render_text_for_column(second_column_attributes, offsets[1], lambda attr: f"{attr.upper()}: {getattr(self.player, attr)}")

        def get_third_column_text(attr):
            if attr in ['region', 'name']:
                room_attrs = f"{getattr(self.player.current_room, attr, 'N/A')}".title()
                return room_attrs.replace('_', ' ')
            elif attr in ['x']:
                player_attr_x = getattr(self.player.current_room, attr, 'N/A')
                player_attr_y = getattr(self.player.current_room, 'y', 'N/A')
                return f"Coords: ({player_attr_x}, {player_attr_y})"
            else: # attr == perc_lit
                perc_lit = self.game_manager.map_visualizer.calculate_percent_lit()
                return f"Map Lit %: {perc_lit:.2f}"

        render_text_for_column(third_column_attributes, offsets[2], get_third_column_text)

        y_offset = self.window_height * 0.02
        equipment_title = "Equipment"
        title_surface = custom_font.render(equipment_title, True, text_color)
        stats_surface.blit(title_surface, (offsets[3] - (title_surface.get_width() // 2), y_offset))
        y_offset += 20
        for equipment in [self.player.equipped_weapon, self.player.equipped_armor]:
            if equipment:
                equipment_surface = custom_font.render(equipment, True, text_color)
                stats_surface.blit(equipment_surface, (offsets[3] - (equipment_surface.get_width() // 2), y_offset))
                y_offset += 20
        half_window_width = self.window_width // 2
        screen.blit(stats_surface, (half_window_width, self.window_height - stats_height))

    def render_middle_button_and_inventory_frame(self, surface, padding):
        section_width = (surface.get_width() - 2 * padding) // 3
        relative_division_y = 0  # Top of the lower_ui_surface
        frame_x = padding
        frame_width = section_width - 2 * padding
        frame_height = surface.get_height() - 2 * padding
        inventory_label = "Inventory"
        label_surface = self.custom_font.render(inventory_label, True, (255, 255, 255))
        surface.blit(label_surface, (frame_x + (frame_width - label_surface.get_width()) // 2, relative_division_y + padding))
        frame_rect = pygame.Rect(frame_x, relative_division_y + label_surface.get_height() + padding, frame_width, frame_height - label_surface.get_height())
        pygame.draw.rect(surface, (144, 236, 144), frame_rect, 1)
        item_start_y = relative_division_y + label_surface.get_height() + 2 * padding
        item_spacing = 20
        self.inventory_item_rects.clear()  # Clear previous rectangles
        for i, item in enumerate(self.player.inventory.items):
            item_text = f"- {item}"
            item_surface = self.custom_font.render(item_text, True, (255, 255, 255))
            item_rect = item_surface.get_rect(topleft=(frame_x + padding, item_start_y + i * item_spacing))
            self.inventory_item_rects.append((item, item_rect))
            surface.blit(item_surface, item_rect.topleft)
        button_width, button_height = 120, 40
        button_x = section_width + (section_width - button_width) // 2
        button_y = (frame_height - button_height) // 2  # Centering the button vertically in the frame
        self.middle_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        self.set_middle_button_text()
        button_label_surface = self.custom_font.render(self.middle_button_label, True, (0, 0, 0))
        label_x = self.middle_button_rect.x + (self.middle_button_rect.width - button_label_surface.get_width()) // 2
        label_y = self.middle_button_rect.y + (self.middle_button_rect.height - button_label_surface.get_height()) // 2
        pygame.draw.rect(surface, (200, 200, 200), self.middle_button_rect)
        surface.blit(button_label_surface, (label_x, label_y))

    def render_direction_buttons(self, surface, padding):
        right_section_start = 2 * ((surface.get_width() - 2 * padding) // 3)
        section_width = (surface.get_width() - 2 * padding) // 3
        button_size = section_width // 5
        button_adjust = 5
        adjusted_button_size = button_size - 2 * button_adjust
        relative_division_y = 0
        center_x = right_section_start + section_width // 2
        center_y = relative_division_y + (surface.get_height() - relative_division_y) // 2
        self.n_button_rect = pygame.Rect(center_x - adjusted_button_size // 2, center_y - button_size - adjusted_button_size // 2, adjusted_button_size, adjusted_button_size)
        self.s_button_rect = pygame.Rect(center_x - adjusted_button_size // 2, center_y + button_size // 2, adjusted_button_size, adjusted_button_size)
        self.w_button_rect = pygame.Rect(center_x - button_size - adjusted_button_size // 2, center_y - adjusted_button_size // 2, adjusted_button_size, adjusted_button_size)
        self.e_button_rect = pygame.Rect(center_x + button_size // 2, center_y - adjusted_button_size // 2, adjusted_button_size, adjusted_button_size)
        black_color = (0, 0, 0)
        buttons = {'N': self.n_button_rect, 'S': self.s_button_rect, 'W': self.w_button_rect, 'E': self.e_button_rect}
        for label, rect in buttons.items():
            pygame.draw.rect(surface, (144, 236, 144), rect)
            label_surface = self.custom_font.render(label, True, black_color)
            surface.blit(label_surface, (rect.centerx - label_surface.get_width() // 2, rect.centery - label_surface.get_height() // 2))

    def process_input(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Mouse wheel up
                    self.message_display.handle_scroll(-1)  # Scroll up
                elif event.button == 5:  # Mouse wheel down
                    self.message_display.handle_scroll(1)   # Scroll down
                mouse_pos = pygame.mouse.get_pos()
                self.check_button_click(mouse_pos)
                self.check_inventory_click(mouse_pos)

    def check_button_click(self, mouse_pos):
        translated_mouse_pos = (mouse_pos[0], mouse_pos[1] - self.window_height * 3 // 4)
        direction = None
        if self.n_button_rect and self.n_button_rect.collidepoint(translated_mouse_pos):
            direction = 'n'
        elif self.s_button_rect and self.s_button_rect.collidepoint(translated_mouse_pos):
            direction = 's'
        elif self.w_button_rect and self.w_button_rect.collidepoint(translated_mouse_pos):
            direction = 'w'
        elif self.e_button_rect and self.e_button_rect.collidepoint(translated_mouse_pos):
            direction = 'e'
        if direction:
            self.game_manager.move_player(direction)
            self.game_manager.enemy_manager.move_enemies()
        if self.middle_button_rect and self.middle_button_rect.collidepoint(translated_mouse_pos):
            self.handle_middle_button_click()

    def check_inventory_click(self, mouse_pos):
        # If there is an offset, adjust mouse_pos accordingly
        offset_y = self.window_height * 3 // 4
        adjusted_mouse_pos = (mouse_pos[0], mouse_pos[1] - offset_y)

        for item, rect in self.inventory_item_rects:
            if rect.collidepoint(adjusted_mouse_pos):
                self.player.inventory.remove_item(item)
                self.player.current_room.decorations.append(item)
                self.message_display.add_message(f"You dropped the {item} on the ground.")
                self.room_display.player_inventory_change = True
                self.room_display.display_room_info(self.screen)
                break

    def set_middle_button_text(self):
        new_state = None
        # Check for enemies
        for enemy in self.game_manager.enemy_manager.enemies:
            if enemy.current_room == self.game_manager.player.current_room:
                new_state = "enemy"
                break
        # Check for items only if no enemy is found
        if new_state is None:
            for item in self.game_manager.player.current_room.decorations:
                if self.item_category_map.get(item, '') in {'T', 'W', 'A', 'K'}:
                    new_state = "item"
                    break
        # Compare new state with current state
        if new_state != self.current_state:
            self.update_button_label_and_sound(new_state)
            self.current_state = new_state

    def update_button_label_and_sound(self, new_state):
        if new_state == "enemy":
            self.middle_button_label = "Attack"
            self.sounds.play_sound('danger', 0.75)
        elif new_state == "item":
            self.middle_button_label = "Pick Up"
            self.sounds.play_sound('inventory', 0.75)
        else:
            self.middle_button_label = ""

    def handle_middle_button_click(self):
        if self.middle_button_label == "Attack":
            self.game_manager.is_combat = True
            self.game_manager.combat = Combat(self.player, True, self.game_manager.enemy_manager, self.message_display)
        
        if self.middle_button_label == "Pick Up":
            for item in self.player.current_room.decorations:
                item_category = self.item_category_map.get(item, '')
                if not self.player.inventory.full:
                    
                    if item_category in {'T', 'K'}:
                        
                        if self.player.inventory.add_item(item):
                            self.room_display.player_inventory_change = True 
                            self.message_display.add_message(f"You picked up the {item}.")
                    
                    if item_category in {'W'} and self.player.equipped_weapon is None:
                        self.room_display.player_inventory_change = True
                        self.player.equip_item(item, item_category)
                        self.message_display.add_message(f"You equipped the {item}.")
                    
                    elif item_category in {'A'} and self.player.equipped_armor is None:
                        self.room_display.player_inventory_change = True
                        self.player.equip_item(item, item_category)
                        self.message_display.add_message(f"You equipped the {item}.")
                    
                    elif item_category in {'W'} and self.player.equipped_weapon is not None:
                        self.room_display.player_inventory_change = True
                        self.message_display.add_message(f"You dropped the {self.player.equipped_weapon}.")
                        self.player.unequip_item(self.player.equipped_weapon, item_category)
                        self.player.equip_item(item, item_category)
                        self.message_display.add_message(f"You equipped the {item}.")
                    
                    elif item_category in {'A'} and self.player.equipped_armor is not None:
                        self.room_display.player_inventory_change = True
                        self.message_display.add_message(f"You dropped the {self.player.equipped_armor}.")
                        self.player.unequip_item(self.player.equipped_armor, item_category)
                        self.message_display.add_message(f"You equipped the {item}.")
                        self.player.equip_item(item, item_category)
                    self.room_display.display_room_info(self.screen)
                
                else:
                    self.message_display.add_message(f"Your inventory is full.")
                break
                
