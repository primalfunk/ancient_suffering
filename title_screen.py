import logging
import pygame
from sound_manager import SoundManager

class TitleScreen:
    def __init__(self, screen, width, height):
        self.player_name = "PLAYER"
        self.sounds = SoundManager()
        self.boot_logger = logging.getLogger('boot')
        self.screen = screen
        self.running = True
        self.font_large = pygame.font.Font(None, 80)
        self.font_small = pygame.font.Font(None, 30)
        self.is_finished = False
        self.width = width
        self.height = height

    def init_music(self, volume):
        pygame.mixer.music.load('music/bgmusic.mp3')
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)  # Loop the music

    def render_text(self):
        title_text = self.font_large.render("The Endless Anguish", True, (211, 211, 211))  # Very light gray color
        title_rect = title_text.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 3))
        
        self.screen.blit(title_text, title_rect)
        border_color = (144, 238, 144)  # Light green border
        pygame.draw.rect(self.screen, border_color, title_rect.inflate(20, 20), 2)
        self.input_box = pygame.Rect(100, 150, 140, 32)
        self.button = pygame.Rect(100, 200, 100, 32)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.active = False
        self.text = ''
        self.font_small = pygame.font.Font(None, 30)

    def update(self):
        self.screen.fill((0, 0, 0))
        self.render_text()
        self.position_ui_elements()
        self.draw_label()
        self.draw_input_box()
        self.draw_button()
        pygame.display.flip()

    def position_ui_elements(self):
        title_rect = self.font_large.render("The Endless Anguish", True, (211, 211, 211)).get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 3))
        title_bottom = title_rect.bottom
        # Horizontal center of the screen
        center_x = self.screen.get_width() / 2
        # Calculate width of each element
        input_box_width = self.input_box.width
        button_width = self.button.width
        label_width = self.font_small.size("What is your name?")[0]  # Get the width of the label text
        # Position the elements
        self.input_box.topleft = (center_x - input_box_width // 2, title_bottom + 80)
        self.button.topleft = (center_x - button_width // 2, title_bottom + 120)
        self.label_pos = (center_x - label_width // 2, title_bottom + 40)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_box.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive

            if self.button.collidepoint(event.pos) and not self.is_finished:
                self.process_start_game()
                return
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.process_start_game()
                    return
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def draw_label(self):
        label = self.font_small.render("What is your name?", True, (211, 211, 211))
        self.screen.blit(label, self.label_pos)

    def draw_input_box(self):
        # Render the current text.
        txt_surface = self.font_small.render(self.text, True, self.color)
        # Resize the box if the text is too long.
        width = max(200, txt_surface.get_width() + 10)
        self.input_box.w = width
        # Blit the text.
        self.screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
        # Blit the input_box rect.
        pygame.draw.rect(self.screen, self.color, self.input_box, 2)

    def draw_button(self):
        # Draw the button rect and label
        pygame.draw.rect(self.screen, self.color_inactive, self.button)
        button_label = self.font_small.render("Start Game", True, (211, 211, 211))
        self.screen.blit(button_label, (self.button.x + 5, self.button.y + 5))

