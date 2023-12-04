import pygame
import random

class UI:
    def __init__(self, screen, player, window_width, window_height):
        self.screen = screen
        self.player = player
        self.window_width = window_width
        self.window_height = window_height
        self.custom_font = pygame.font.Font('customfont.ttf', 22)
        self.last_room_id = None
        self.to_render = []

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
        lines.append(current_line)  # Add the last line

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
        start_y = padding  # Initial Y position with padding

        for line in self.to_render:
            wrapped_lines = self.wrap_text(line, container_width)
            for wrapped_line in wrapped_lines:
                text_surface = self.custom_font.render(wrapped_line, True, (255, 255, 255))
                center_x = padding + (container_width - text_surface.get_width()) // 2
                room_info_surface.blit(text_surface, (center_x, start_y))
                start_y += self.custom_font.size(wrapped_line)[1]

        border_color = (144, 238, 144)
        border_width = 1
        pygame.draw.rect(room_info_surface, border_color, room_info_surface.get_rect(), border_width)
        self.screen.blit(room_info_surface, (0, 0))

    def update_room_info_text(self):
        being = ['find yourself in ', 'are in ', 'have reached ', 'have arrived at ', 'are standing in ']
        room_name = self.player.current_room.name.lower() if self.player.current_room.name else "unknown place"
        region_name = self.player.current_room.region.lower() if self.player.current_room.region else "unknown region"
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