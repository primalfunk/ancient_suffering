import pygame

class MessageDisplay:
    def __init__(self, x, y, width, height, font):
        self.messages = []
        self.max_messages = 100
        self.x = x
        self.horizontal_pad = 20
        self.vertical_pad = 20
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.scroll_pos = 0

    def add_message(self, message):
        if len(self.messages) >= self.max_messages:
            self.messages.pop(0)
        self.messages.append(message)
        total_text_height = len(self.messages) * self.font.get_height() + self.vertical_pad
        if total_text_height > self.height:
            num_visible_lines = (self.height - self.vertical_pad) // self.font.get_height()
            self.scroll_pos = len(self.messages) - num_visible_lines
        else:
            self.scroll_pos = 0

    def handle_scroll(self, scroll_amount):
        self.scroll_pos += scroll_amount
        self.scroll_pos = max(0, min(self.scroll_pos, len(self.messages) - 1))

    def render(self, surface):
        surface_area = pygame.Rect(self.x, self.y, self.width, self.height)
        surface.set_clip(surface_area)

        y_offset = self.y + self.vertical_pad - self.scroll_pos * self.font.get_height()
        for message in self.messages:
            wrapped_lines = self.wrap_text(message, self.width - self.horizontal_pad)
            for line in wrapped_lines:
                if y_offset >= self.y + self.height:
                    break
                text_surface = self.font.render(line, True, (255, 255, 255))
                surface.blit(text_surface, (self.x + self.horizontal_pad, y_offset))
                y_offset += self.font.get_height()
                if y_offset + self.vertical_pad >= self.y + self.height:
                    break

        # Draw a single line at the top of the message area
        line_color = (144, 236, 144)
        pygame.draw.line(surface, line_color, (self.x, self.y), (self.x + self.width, self.y), 2)  # Line thickness set to 2

        surface.set_clip(None)

    def wrap_text(self, text, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            if self.font.size(current_line + word)[0] <= max_width:
                current_line += word + ' '
            else:
                lines.append(current_line)
                current_line = word + ' '
        lines.append(current_line)
        return lines

    def draw_top_border(surface, rect, color, border_width):
        # Draw only the top border
        pygame.draw.line(surface, color, rect.topleft, rect.topright, border_width)
