import pygame

class TitleScreen:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.init_music()
        self.font_large = pygame.font.Font(None, 100)  # Large font for the title
        self.font_small = pygame.font.Font(None, 50)  # Smaller font for the instruction

    def init_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load('bgmusic.mp3')
        pygame.mixer.music.play(-1)  # Loop the music

    def render_text(self):
        title_text = self.font_large.render("The Endless Anguish", True, (211, 211, 211))  # Very light gray color
        instruction_text = self.font_small.render("Press any key to continue", True, (211, 211, 211))

        # Center the text
        title_rect = title_text.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 3))
        instruction_rect = instruction_text.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2))

        # Draw the texts
        self.screen.blit(title_text, title_rect)
        self.screen.blit(instruction_text, instruction_rect)

        # Draw a border around the title
        border_color = (144, 238, 144)  # Light green border
        pygame.draw.rect(self.screen, border_color, title_rect.inflate(20, 20), 2)  # Adjust padding as needed

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    pygame.mixer.music.stop()  
                    self.running = False  # Any key press ends the title loop

            self.screen.fill((0, 0, 0))  # Fill the screen with black or your chosen background color
            self.render_text()
            pygame.display.flip()
