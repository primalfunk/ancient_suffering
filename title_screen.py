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
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.width = width
        self.height = height
        self.placeholder_text = 'PLAYER'
        self.cursor_visible = False
        self.cursor_timer = pygame.time.get_ticks() 
        self.button_color = self.color_inactive 
        self.active = True
        self.text = "PLAYER"

    def init_music(self, volume):
        pygame.mixer.music.load('music/bgmusic.mp3')
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

    def render_text(self):
        title_text = self.font_large.render("The Endless Anguish", True, (211, 211, 211))  # Very light gray color
        self.title_rect = title_text.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 3))
        self.screen.blit(title_text, self.title_rect)
        border_color = (144, 238, 144)  # Light green border
        pygame.draw.rect(self.screen, border_color, self.title_rect.inflate(20, 20), 2)
        self.input_box = pygame.Rect(100, 150, 140, 32)
        self.button = pygame.Rect(100, 200, 100, 32)
        self.color = self.color_inactive
        self.font_small = pygame.font.Font(None, 30)

    def position_ui_elements(self):
        title_bottom = self.title_rect.bottom
        center_x = self.screen.get_width() / 2
        input_box_width = self.input_box.width
        button_width = self.button.width
        label_width = self.font_small.size("What is your name?")[0]
        self.input_box.topleft = (center_x - input_box_width // 2, title_bottom + 80)
        self.button.topleft = (center_x - button_width // 2, title_bottom + 120)
        self.label_pos = (center_x - label_width // 2, title_bottom + 40)

    def draw_label(self):
        label = self.font_small.render("What is your name?", True, (211, 211, 211))
        self.screen.blit(label, self.label_pos)

    def draw_input_box(self):
        current_text = self.text if self.active else self.placeholder_text
        txt_color = self.color if self.active else pygame.Color('grey')  # Use grey color for placeholder
        txt_surface = self.font_small.render(current_text, True, txt_color)
        width = max(200, txt_surface.get_width() + 10)
        self.input_box.w = width
        box_color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(self.screen, box_color, self.input_box)
        self.screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
        if self.active and self.cursor_visible:
            cursor_x = self.input_box.x + txt_surface.get_width() + 5
            cursor_y = self.input_box.y + 5
            cursor_rect = pygame.Rect(cursor_x, cursor_y, 2, self.font_small.get_height())
            pygame.draw.rect(self.screen, self.color, cursor_rect)

    def draw_button(self):
        pygame.draw.rect(self.screen, self.button_color, self.button)
        button_label = self.font_small.render("Start", True, (211, 211, 211))
        self.screen.blit(button_label, (self.button.x + 5, self.button.y + 5))

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
            print(f"Mouse click at {event.pos}") 
            if self.input_box.collidepoint(event.pos):
                if not self.active: 
                    self.text = ''
                self.active = True
            else:
                self.active = False
            print(f"Input box active state: {self.active}")
            if self.button.collidepoint(event.pos) and not self.is_finished:
                self.process_start_game()
                return
