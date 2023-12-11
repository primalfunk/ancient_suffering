import logging
import math
import pygame
import random
from sound_manager import SoundManager

class TitleScreen:
    def __init__(self, screen, width, height):
        self.player_name = "PLAYER"
        self.sounds = SoundManager()
        self.boot_logger = logging.getLogger('boot')
        self.border_color = (0, 255, 0)
        self.screen = screen
        self.running = True
        self.font_large = pygame.font.Font('fonts/title.ttf', 100) 
        self.font_small = pygame.font.Font('fonts/messages.ttf', 50)
        self.is_finished = False
        self.color_inactive = pygame.Color(20, 20, 100)
        self.color_active = pygame.Color(110, 110, 200)
        self.color_direction = 1
        self.current_title_color = 255
        self.current_border_color = 255
        self.width = width
        self.height = height
        self.placeholder_text = ''
        self.cursor_visible = False
        self.cursor_timer = pygame.time.get_ticks() 
        self.button_color = self.color_inactive 
        self.active = True
        self.text = "PLAYER"
        self.random_color = self.get_random_color()

    def get_random_color(self):
        r = random.randint(35, 95)
        g = random.randint(55, 95)
        b = random.randint(75, 95)
        random_color = (r, g, b)
        return random_color
    
    def render_text(self):
        # Update the color values
        self.current_title_color += self.color_direction * 1.2  # Adjust speed as needed
        if self.current_title_color > 255:
            self.current_title_color, self.color_direction = 255, -1
        elif self.current_title_color < 0:
            self.current_title_color, self.color_direction = 0, 1
        animated_title_color = (self.current_title_color, 70, 70)
        animated_border_color = (70, 255 - self.current_title_color, 70)
        offset_color_value = (self.current_title_color + 128) % 256  # Offset by 128
        animated_second_border_color = (70, 70, 255 - offset_color_value)
        title_text = self.font_large.render("The Lords of Chaos", True, animated_title_color)
        self.title_rect = title_text.get_rect(center=(self.width / 2, self.height / 3))
        self.screen.blit(title_text, self.title_rect)
        title_border_rect = self.title_rect.inflate(20, 20)
        pygame.draw.rect(self.screen, animated_border_color, title_border_rect, 2)
        second_title_border_rect = self.title_rect.inflate(24, 24)  # Inflate by an additional 2 pixels on each side
        pygame.draw.rect(self.screen, animated_second_border_color, second_title_border_rect, 2)

        self.position_ui_elements()
        self.draw_label()
        self.draw_input_box()
        self.draw_button()

    def position_ui_elements(self):
        title_border_rect = self.title_rect.inflate(20, 20)
        padding = 40
        self.label_pos = (title_border_rect.left, title_border_rect.bottom + padding)
        input_box_width = 200
        label_width, label_height = self.font_small.size("What is your name?")
        input_box_x = self.label_pos[0] + label_width + 10
        input_box_y = self.label_pos[1]
        self.input_box = pygame.Rect(input_box_x, input_box_y, input_box_width, label_height)
        button_width = 200
        button_height = label_height
        button_x = self.width / 2 - button_width / 2
        button_y = input_box_y + label_height + padding
        self.button = pygame.Rect(button_x, button_y, button_width, button_height)

    def draw_input_box(self):
        current_text = self.text if self.active else self.placeholder_text
        txt_color = self.color_active if self.active else self.color_inactive
        txt_surface = self.font_small.render(current_text, True, txt_color)
        text_y = self.input_box.y + (self.input_box.height - txt_surface.get_height()) / 2
        self.screen.blit(txt_surface, (self.input_box.x + 5, text_y))
        if self.active and self.cursor_visible:
            cursor_x = self.input_box.x + txt_surface.get_width() + 5
            cursor_height = self.font_small.get_height()
            cursor_y = self.input_box.y + (self.input_box.height - cursor_height) / 2
            cursor_rect = pygame.Rect(cursor_x, cursor_y, 2, cursor_height)
            pygame.draw.rect(self.screen, pygame.Color('white'), cursor_rect)
    
    def draw_label(self):
        label_text = "What is your name?"
        label = self.font_small.render(label_text, True, (200, 200, 200))
        self.screen.blit(label, self.label_pos)

    def draw_button(self):
        pygame.draw.rect(self.screen, self.button_color, self.button)
        button_label = self.font_small.render("Start", True, pygame.Color('white'))
        button_label_rect = button_label.get_rect(center=self.button.center)
        self.screen.blit(button_label, button_label_rect.topleft)

    def process_start_game(self):
        self.player_name = self.text if self.text else "PLAYER"
        self.is_finished = True

    def toggle_cursor(self):
        if pygame.time.get_ticks() - self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = pygame.time.get_ticks()

    def update(self):
            self.screen.fill((0, 0, 0))
            self.render_text()
            self.position_ui_elements()
            self.draw_label()
            self.draw_input_box()
            self.draw_button()
            self.toggle_cursor()
            mouse_pos = pygame.mouse.get_pos()
            if self.button.collidepoint(mouse_pos):
                self.button_color = self.color_active
            else:
                self.button_color = self.color_inactive
            pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.process_start_game()
                return
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_box.collidepoint(event.pos):
                if not self.active: 
                    self.text = ''
                self.active = True
            else:
                self.active = False
            if self.button.collidepoint(event.pos) and not self.is_finished:
                self.process_start_game()
                return
            
    def init_music(self, volume):
        pygame.mixer.music.load('music/bgmusic.mp3')
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

