import pygame
import random

class RoomDisplay:
    def __init__(self, screen, player, custom_font, window_dimensions):
        self.screen = screen
        self.player = player
        self.custom_font = custom_font
        self.window_width, self.window_height = window_dimensions
        self.last_room_id = None
        self.player_inventory_change = False
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
        lines.append(current_line)
        return lines

    def display_room_info(self, screen):
        current_room_id = (self.player.current_room.x, self.player.current_room.y)
        if current_room_id != self.last_room_id or self.player_inventory_change:
            self.update_room_info_text()
            self.last_room_id = current_room_id
            self.player_inventory_change = False
        room_info_surface = pygame.Surface((self.window_width // 2, self.window_height))
        room_info_surface.fill((0, 0, 0))
        padding = 10
        container_width = self.window_width // 2 - 2 * padding
        division_y = self.window_height * 3 // 4
        pygame.draw.line(room_info_surface, (144, 238, 144), (0, division_y), (self.window_width // 2, division_y), 1)
        self.render_room_text(room_info_surface, container_width, padding, division_y)
        border_color = (144, 238, 144)
        pygame.draw.rect(room_info_surface, border_color, room_info_surface.get_rect(), 1)
        screen.blit(room_info_surface, (0, 0))

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
        enemy_desc = ""
        enemies = self.player.current_room.enemies
        if len(enemies) > 1:
            enemy_desc = f"There are {len(enemies)} enemies in this room."
        elif len(enemies) == 1:
            enemy = enemies[0]
            enemy_desc = f"There is "+ self.article_for_word(enemy.name) + enemy.name + " here."
        self.to_render = [region_desc, items_desc, enemy_desc]

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
    
    def article_for_word(self, word):
        if word[0].lower() in 'aeiou':
            return "an "
        else:
            return "a "