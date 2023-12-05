import pygame
from message_display import MessageDisplay
from room_display import RoomDisplay

class UI:
    def __init__(self, screen, player, window_width, window_height, game_manager):
        self.screen = screen
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
        message_display_height = 300  # Adjust as needed
        print(f"message display at x {0} y {self.window_height // 2 - message_display_height} width {self.window_width // 2} height {message_display_height}")
        self.message_display = MessageDisplay(
            x=0, 
            y=2*self.window_height // 3 - message_display_height, 
            width=self.window_width // 2, 
            height=message_display_height,
            font=self.custom_font
        )

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
        self.render_player_stats()
        self.message_display.render(self.screen)

    def render_player_stats(self):
        custom_font = pygame.font.Font('customfont.ttf', 20)
        stats_surface = pygame.Surface((self.window_height - 160, 160))
        stats_surface.fill((50, 50, 50))
        first_column_attributes = ['name', 'level', 'hp', 'mp', 'exp']
        second_column_attributes = ['str', 'dex', 'int', 'wis', 'con', 'cha']
        third_column_attributes = ['x', 'y']
        quarter_width = (self.window_width // 2) // 4
        first_column_offset = quarter_width - (quarter_width // 2)
        second_column_offset = 2 * quarter_width - (quarter_width // 2)
        third_column_offset = 3 * quarter_width - (quarter_width // 2)
        fourth_column_offset = 4 * quarter_width - (quarter_width // 2)
        first_column_color = (135, 206, 235)  # soft blue
        second_column_color = (152, 251, 152)  # pale green
        third_column_color = (230, 230, 250)  # lavender
        fourth_area_color = (255, 253, 208) # cream
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
            text_x = first_column_offset - (text_surface.get_width() // 2)
            stats_surface.blit(text_surface, (text_x, 20 * i))
        for i, attr in enumerate(second_column_attributes):
            text = f"{attr.upper()}: {getattr(self.player, attr)}"
            text_surface = custom_font.render(text, True, second_column_color)
            text_x = second_column_offset - (text_surface.get_width() // 2)
            stats_surface.blit(text_surface, (text_x, 20 * i))
        for i, attr in enumerate(third_column_attributes):
            text = f"Lat: {getattr(self.player, 'x')}" if attr == 'x' else f"Lon: {getattr(self.player, 'y')}"
            text_surface = custom_font.render(text, True, third_column_color)
            text_x = third_column_offset - (text_surface.get_width() // 2)
            stats_surface.blit(text_surface, (text_x, 20 * i))
        half_window_width = self.window_width // 2
        self.screen.blit(stats_surface, (half_window_width, self.window_height - 160))

    def render_middle_button_and_inventory_frame(self, surface, padding):
        section_width = (surface.get_width() - 2 * padding) // 3
        # Relative division_y for lower_ui_surface
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
        # item in inventory collision rects
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
            self.game_manager.move_enemies()
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
                self.room_display.display_room_info()
                break

    def set_middle_button_text(self):
        special_items = {"amulet", "statue", "scroll", "gemstone", "relic", "backpack", "wood", "gold", "lantern", "flint"}
        self.middle_button_label = ""
        for item in self.player.current_room.decorations:
            if item in special_items:
                self.middle_button_label = "Pick Up"
                break

    def handle_middle_button_click(self):
        if self.middle_button_label == "Pick Up":
            special_items = {"amulet", "statue", "scroll", "gemstone", "relic", "backpack", "wood", "gold", "lantern", "flint"}
            for item in self.player.current_room.decorations:
                if item in special_items:
                    if self.player.inventory.add_item(item):
                        self.player.current_room.decorations.remove(item)
                        self.room_display.player_inventory_change = True
                        self.message_display.add_message(f"You picked up the {item}.")
                        self.room_display.display_room_info()
                        break
                    else:
                        self.message_display.add_message(f"Unable to pick up {item}. Your inventory is full.")
                        break
        else:
            if len(self.player.current_room.decorations) > 0:
                self.message_display.add_message(f"Sorry, you cannot have the {self.player.current_room.decorations[0]}.")