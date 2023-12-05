import pygame
import random

class UI:
    def __init__(self, screen, player, window_width, window_height, game_manager):
        self.screen = screen
        self.n_button_rect = None
        self.s_button_rect = None
        self.w_button_rect = None
        self.e_button_rect = None
        self.middle_button_rect = None
        self.player = player
        self.window_width = window_width
        self.window_height = window_height
        self.custom_font = pygame.font.Font('customfont.ttf', 22)
        self.last_room_id = None
        self.to_render = []
        self.game_manager = game_manager

    def wrap_text(self, text, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''
        
        for word in words:
            # Check if adding the word exceeds the max width
            if self.custom_font.size(current_line + word)[0] <= max_width:
                current_line += word + ' '
            else:
                lines.append(current_line)
                current_line = word + ' '
        lines.append(current_line)

        return lines

    def display_room_info(self):
        current_room_id = (self.player.current_room.x, self.player.current_room.y)
        if current_room_id != self.last_room_id:
            self.update_room_info_text()
            self.last_room_id = current_room_id
        room_info_surface = pygame.Surface((self.window_width // 2, self.window_height))
        room_info_surface.fill((0, 0, 0))
        padding = 10  # Padding inside the container
        container_width = self.window_width // 2 - 2 * padding
        division_y = self.window_height * 3 // 4  # Division point
        pygame.draw.line(room_info_surface, (255, 255, 255), (0, division_y), (self.window_width // 2, division_y), 1)
        self.render_room_text(room_info_surface, container_width, padding, division_y)
        self.render_button_and_inventory_frame(room_info_surface, division_y, padding)
        border_color = (144, 238, 144)
        self.render_direction_buttons(room_info_surface, division_y, padding)

        pygame.draw.rect(room_info_surface, border_color, room_info_surface.get_rect(), 1)
        self.screen.blit(room_info_surface, (0, 0))

    def update_room_info_text(self):
        being = ['find yourself in ', 'are in ', 'have reached ', 'have arrived at ', 'are standing in ']
        room_name = self.player.current_room.name.lower() if self.player.current_room.name else "unknown place"
        region_name = self.player.current_room.region.replace('_', ' ') if self.player.current_room.region else "unknown region"
        region_name = region_name.lower()
        items = self.player.current_room.decorations
        region_desc = f"You {random.choice(being)}{self.article_for_word(room_name)}{room_name} in {self.article_for_word(region_name)}{region_name}."
        if items:
            items_desc = "You see "
            if len(items) == 1:
                # Handle single item
                items_desc += self.article_for_word(items[0]) + items[0] + "."
            else:
                # Handle multiple items
                items_desc += ", ".join([self.article_for_word(item) + item for item in items[:-1]])
                items_desc += " and " + self.article_for_word(items[-1]) + items[-1] + "."
        else:
            items_desc = "You see nothing of interest."
        self.to_render = [region_desc, items_desc]

    def article_for_word(self, word):
        if word[0].lower() in 'aeiou':
            return "an "
        else:
            return "a "

    def display_player_stats(self):
        custom_font = pygame.font.Font('customfont.ttf', 20)
        stats_surface = pygame.Surface((self.window_height - 160, 160))
        stats_surface.fill((50, 50, 50))
        first_column_attributes = ['name', 'level', 'hp', 'mp', 'exp']
        second_column_attributes = ['str', 'dex', 'int', 'wis', 'con', 'cha']
        third_column_attributes = ['x', 'y']
        for i, attr in enumerate(first_column_attributes):
            color = (170, 190, 255)
            text = f"{attr.upper()}: {getattr(self.player, attr)}"
            text_surface = custom_font.render(text, True, color)
            stats_surface.blit(text_surface, (10, 20 * i))
        # Render second column
        column_offset = self.window_width // 6  # Horizontal offset for the second column
        for i, attr in enumerate(second_column_attributes):
            text = f"{attr.upper()}: {getattr(self.player, attr)}"
            text_surface = custom_font.render(text, True, (170, 190, 255))  # White text
            stats_surface.blit(text_surface, (column_offset, 20 * i))
        # Render third column
        column_offset = self.window_width // 3 # Horizontal offset for the second column
        for i, attr in enumerate(third_column_attributes):
            if attr == 'x':
                text = f"LATITUDE: {getattr(self.player, attr)}"
            elif attr == 'y':
                text = f"LONGITUDE: {getattr(self.player, attr)}"
            else:
                text = f"{attr.upper()}: {getattr(self.player, attr)}"
            text_surface = custom_font.render(text, True, (170, 190, 255))  # White text
            stats_surface.blit(text_surface, (column_offset, 20 * i))
        # Blit the stats surface onto the main screen
        half_window_width = self.window_width // 2
        self.screen.blit(stats_surface, (half_window_width, self.window_height - 160))

    def render_room_text(self, surface, container_width, padding, division_y):
        start_y = padding
        for line in self.to_render:
            wrapped_lines = self.wrap_text(line, container_width)
            for wrapped_line in wrapped_lines:
                text_surface = self.custom_font.render(wrapped_line, True, (255, 255, 255))
                center_x = padding + (container_width - text_surface.get_width()) // 2
                surface.blit(text_surface, (center_x, start_y))
                start_y += self.custom_font.size(wrapped_line)[1]
                if start_y > division_y - padding: break

    def render_button_and_inventory_frame(self, surface, division_y, padding):
        section_width = (surface.get_width() - 2 * padding) // 3
        line_color = (255, 255, 255)
        pygame.draw.line(surface, line_color, (section_width, division_y), (section_width, surface.get_height()), 1)
        pygame.draw.line(surface, line_color, (2 * section_width, division_y), (2 * section_width, surface.get_height()), 1)
        frame_x = padding
        frame_width = section_width - 2 * padding
        frame_height = surface.get_height() - division_y - 2 * padding
        inventory_label = "Inventory"
        label_surface = self.custom_font.render(inventory_label, True, (255, 255, 255))
        surface.blit(label_surface, (frame_x + (frame_width - label_surface.get_width()) // 2, division_y + padding))
        frame_rect = pygame.Rect(frame_x, division_y + label_surface.get_height() + padding, frame_width, frame_height - label_surface.get_height())
        pygame.draw.rect(surface, (200, 200, 200), frame_rect, 1)
        button_width, button_height = 120, 40
        button_x = section_width + (section_width - button_width) // 2
        button_y = division_y + (frame_height - button_height) // 2
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(surface, (200, 200, 200), button_rect)

    def render_direction_buttons(self, surface, division_y, padding):
        right_section_start = 2 * ((surface.get_width() - 2 * padding) // 3)
        section_width = (surface.get_width() - 2 * padding) // 3
        button_size = section_width // 5  # Square buttons size
        button_adjust = 5  # Adjust button size smaller by 5 pixels on each side
        adjusted_button_size = button_size - 2 * button_adjust

        center_x = right_section_start + section_width // 2
        center_y = division_y + (surface.get_height() - division_y) // 2

        # Define button positions and create rects with adjusted sizes
        self.n_button_rect = pygame.Rect(center_x - adjusted_button_size // 2, center_y - button_size - adjusted_button_size // 2, adjusted_button_size, adjusted_button_size)
        self.s_button_rect = pygame.Rect(center_x - adjusted_button_size // 2, center_y + button_size // 2, adjusted_button_size, adjusted_button_size)
        self.w_button_rect = pygame.Rect(center_x - button_size - adjusted_button_size // 2, center_y - adjusted_button_size // 2, adjusted_button_size, adjusted_button_size)
        self.e_button_rect = pygame.Rect(center_x + button_size // 2, center_y - adjusted_button_size // 2, adjusted_button_size, adjusted_button_size)

        # Draw the buttons and their labels
        black_color = (0, 0, 0)  # Black color for text
        buttons = {'N': self.n_button_rect, 'S': self.s_button_rect, 'W': self.w_button_rect, 'E': self.e_button_rect}
        for label, rect in buttons.items():
            pygame.draw.rect(surface, (200, 200, 200), rect)  # Button color
            label_surface = self.custom_font.render(label, True, black_color)  # Black text color
            surface.blit(label_surface, (rect.centerx - label_surface.get_width() // 2, rect.centery - label_surface.get_height() // 2))


    def process_input(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.check_button_click(mouse_pos)

    def check_button_click(self, mouse_pos):
        # Check if any direction button was clicked
        if self.n_button_rect and self.n_button_rect.collidepoint(mouse_pos):
            self.game_manager.move_player('n')
        elif self.s_button_rect and self.s_button_rect.collidepoint(mouse_pos):
            self.game_manager.move_player('s')
        elif self.w_button_rect and self.w_button_rect.collidepoint(mouse_pos):
            self.game_manager.move_player('w')
        elif self.e_button_rect and self.e_button_rect.collidepoint(mouse_pos):
            self.game_manager.move_player('e')
        # Check for middle button click
        if self.middle_button_rect and self.middle_button_rect.collidepoint(mouse_pos):
            print("Hit middle button")
