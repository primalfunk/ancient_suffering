from combat import Combat
import json
import logging
import pygame
from message_display import MessageDisplay
from room_display import RoomDisplay
from sound_manager import SoundManager

class UI: 
    def __init__(self, screen, player, window_width, window_height, game_manager):
        boot_logger = logging.getLogger('boot')
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
        self.custom_font = pygame.font.Font('customfont.ttf', 21)
        self.last_room_id = None
        self.to_render = []
        self.game_manager = game_manager
        self.room_display = RoomDisplay(screen, player, self.custom_font, (window_width, window_height))
        message_display_height = 300
        self.message_display = MessageDisplay(
            x=0, 
            y=2*self.window_height // 3 - message_display_height, 
            width=self.window_width // 2, 
            height=message_display_height,
            font=self.custom_font
        )
        self.item_category_map = self.parse_item_categories()
        self.current_state = None


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
        # Draw the border around the lower_ui_surface
        border_color = (144, 238, 144)
        pygame.draw.rect(lower_ui_surface, border_color, lower_ui_surface.get_rect(), 2)
        self.screen.blit(lower_ui_surface, (0, self.window_height * 3 // 4))
        self.render_player_stats(self.screen)
        self.message_display.render(self.screen)

    def render_player_stats(self, screen):
        custom_font = pygame.font.Font('customfont.ttf', 20)
        stats_surface = pygame.Surface((self.window_height - 160, 160))
        stats_surface.fill((50, 50, 50))
        first_column_attributes = ['name', 'level', 'hp', 'mp', 'exp']
        second_column_attributes = ['atk', 'defn', 'int', 'wis', 'con', 'eva']
        third_column_attributes = ['x', 'y']
        quarter_width = (self.window_width // 2) // 4
        first_column_offset = quarter_width - (quarter_width // 2)
        second_column_offset = 2 * quarter_width - (quarter_width // 2)
        third_column_offset = 3 * quarter_width - (quarter_width // 2)
        fourth_column_offset = 4 * quarter_width - (quarter_width // 2)
        first_column_color = (135, 206, 235)  # soft blue
        second_column_color = (152, 251, 152)  # pale green
        third_column_color = (230, 230, 250)  # lavender
        fourth_area_color = (255, 253, 208)  # cream
        # Drawing column borders
        def draw_column_border(x_offset, color):
            border_rect = pygame.Rect(x_offset - quarter_width // 2, 0, quarter_width, 160)
            pygame.draw.rect(stats_surface, color, border_rect, 2)
        draw_column_border(first_column_offset, first_column_color)
        draw_column_border(second_column_offset, second_column_color)
        draw_column_border(third_column_offset, third_column_color)
        draw_column_border(fourth_column_offset, fourth_area_color)
        for i, attr in enumerate(first_column_attributes):
            text = f"{attr.title()}: {getattr(self.player, attr)}"
            text_surface = custom_font.render(text, True, first_column_color)
            stats_surface.blit(text_surface, (first_column_offset - (text_surface.get_width() // 2), 20 * i))
        for i, attr in enumerate(second_column_attributes):
            text = f"{attr.upper()}: {getattr(self.player, attr)}"
            text_surface = custom_font.render(text, True, second_column_color)
            stats_surface.blit(text_surface, (second_column_offset - (text_surface.get_width() // 2), 20 * i))
        for i, attr in enumerate(third_column_attributes):
            text = f"Lat: {getattr(self.player, 'x')}" if attr == 'x' else f"Lon: {getattr(self.player, 'y')}"
            text_surface = custom_font.render(text, True, third_column_color)
            stats_surface.blit(text_surface, (third_column_offset - (text_surface.get_width() // 2), 20 * i))
        y_offset = 20  # Starting Y offset for the equipment title
        equipment_title = "Equipment"
        title_surface = custom_font.render(equipment_title, True, fourth_area_color)
        stats_surface.blit(title_surface, (fourth_column_offset - (title_surface.get_width() // 2), y_offset))
        y_offset += 20
        if self.player.equipped_weapon:
            weapon_text = f"{self.player.equipped_weapon}"
            weapon_surface = custom_font.render(weapon_text, True, fourth_area_color)
            stats_surface.blit(weapon_surface, (fourth_column_offset - (weapon_surface.get_width() // 2), y_offset))
            y_offset += 20
        if self.player.equipped_armor:
            armor_text = f"{self.player.equipped_armor}"
            armor_surface = custom_font.render(armor_text, True, fourth_area_color)
            stats_surface.blit(armor_surface, (fourth_column_offset - (armor_surface.get_width() // 2), y_offset))
        half_window_width = self.window_width // 2
        screen.blit(stats_surface, (half_window_width, self.window_height - 160))

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
        pygame.draw.rect(surface, (200, 200, 200), frame_rect, 1)
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
            pygame.draw.rect(surface, (200, 200, 200), rect)
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
            self.game_manager.combat = Combat(self.player, True, self.game_manager.enemy_manager, self.message_display) # attacker, is_player, enemy_manager, message_system
        if self.middle_button_label == "Pick Up":
            for item in self.player.current_room.decorations:
                item_category = self.item_category_map.get(item, '')
                if item_category in {'T', 'K'}:
                    if self.player.inventory.add_item(item):
                        self.player.current_room.decorations.remove(item)
                        self.room_display.player_inventory_change = True
                        self.message_display.add_message(f"You picked up the {item}.")
                    else:
                        self.message_display.add_message(f"Unable to pick up {item}. Your inventory is full.")
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
                break
