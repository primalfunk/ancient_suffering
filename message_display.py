import pygame

class MessageDisplay:
    def __init__(self, x, y, width, height, font):
        self.messages = []
        self.max_messages = 1000
        self.x = x
        self.horizontal_pad = 20
        self.vertical_pad = 5
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.scroll_pos = 0

    def add_message(self, message, color=(0, 0, 0)):
        # Convert message to tuple if it's not already one
        if not isinstance(message, tuple):
            message = (message, color)
        
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        visible_lines = (self.height - self.vertical_pad * 2) // self.font.get_height()
        total_lines = sum(len(self.wrap_text(msg, self.width - self.horizontal_pad * 2)) for msg, _ in self.messages)
        self.scroll_pos = max(0, total_lines - visible_lines)
   
    def render(self, surface):
        message_area = pygame.Rect(self.x, self.y, self.width, self.height)
        surface_area = pygame.Rect(self.x, self.y, self.width, self.height)
        background_color = (255, 255, 255)  # white
        surface.fill(background_color, message_area)
        surface.set_clip(surface_area)
        y_offset = self.y + self.vertical_pad - self.scroll_pos * self.font.get_height()
        for message, color in self.messages:
            wrapped_lines = self.wrap_text(message, self.width - self.horizontal_pad * 2)
            for line in wrapped_lines:
                text_surface = self.font.render(line, True, color)
                text_height = text_surface.get_height()
                surface.blit(text_surface, (self.x + self.horizontal_pad, y_offset))
                y_offset += text_height
        pygame.draw.line(surface, (144, 236, 144), (self.x, self.y), (self.x + self.width, self.y), 2)
        self.draw_scrollbar(surface)
        surface.set_clip(None)

    def draw_scrollbar(self, surface):
        scrollbar_width = 10  # Width of the scrollbar
        scroll_area_height = self.height - 2 * self.vertical_pad
        scrollbar_x = self.x + self.width - scrollbar_width - self.horizontal_pad
        # Calculate total content height
        total_content_height = len(self.messages) * self.font.get_height()
        # Check to prevent division by zero
        if total_content_height == 0:
            return  # No scrollbar needed if there are no messages
        # Calculate scrollbar height
        scrollbar_height = min(self.height, max(20, (scroll_area_height ** 2) / total_content_height))
        # Calculate scrollbar position
        scrollbar_y = self.y + self.vertical_pad + (self.scroll_pos / len(self.messages)) * (scroll_area_height - scrollbar_height)
        scrollbar_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(surface, (144, 236, 144), scrollbar_rect)

    def wrap_text(self, text_tuple, max_width):
        # Unpack the text only if it's a tuple
        text = text_tuple[0] if isinstance(text_tuple, tuple) else text_tuple
        
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            # Build a line with words until it exceeds max_width
            line_test = ' '.join(current_line + [word])
            line_width, _ = self.font.size(line_test)
            if line_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def draw_top_border(surface, rect, color, border_width):
        # Draw only the top border
        pygame.draw.line(surface, color, rect.topleft, rect.topright, border_width)

    def handle_scroll(self, scroll_amount):
        self.scroll_pos += scroll_amount
        total_lines = sum(len(self.wrap_text(message, self.width - self.horizontal_pad * 2)) for message in self.messages)
        self.scroll_pos = max(0, min(self.scroll_pos, total_lines - 1))
