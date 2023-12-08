import logging_config
import pygame
import tkinter as tk
from title_screen import TitleScreen
from game_manager import GameManager

if __name__ == "__main__":
    logging_config.setup_logging()
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_x = (screen_width - screen_width) // 2
    position_y = (screen_height - screen_height) // 2
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((1600, 900))

    title_screen = TitleScreen(screen)
    game_manager = GameManager(screen)
    fade_in_done = False

    # Main game loop
    title_screen.init_music(0.75)
    current_state = game_manager.current_state
    while True:
        if current_state == "title_screen":
            title_screen.update()
            if title_screen.is_finished():
                current_state = "fade_in"

        elif current_state == "fade_in" and not fade_in_done:
            fade_surface = pygame.Surface((game_manager.window_width, game_manager.window_height))
            fade_surface.fill((0, 0, 0)) # black
            for a in range(255, -1, -5): # fade in by lowering the opacity of the overlaying surface
                game_manager.draw_initial_ui_onto_surface(screen)
                fade_surface.set_alpha(a)
                screen.blit(fade_surface, (0, 0))
                pygame.display.flip()
                pygame.time.delay(35)
            fade_in_done = True
            current_state = 'game_loop'
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.3)

        elif current_state == 'game_loop':
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_manager.toggle_fullscreen()
                    elif event.key == pygame.K_r:
                        game_manager.restart_game()
                    else:
                        game_manager.process_keypress(event)
                if game_manager.check_for_combat():
                    current_state = 'combat'
                    pygame.mixer.music.stop()
                    game_manager.combat.init_music(volume=0.7)
                game_manager.ui.process_input(events)

            if current_state != 'combat':
                game_manager.update()
                pygame.display.flip()

        elif current_state == 'combat':
            game_manager.combat.update()
            game_manager.update()
            events = pygame.event.get()
            game_manager.ui.process_input(events)
            if game_manager.combat.is_over:
                pygame.mixer.music.stop()
                game_manager.combat.resume_regular_music()
                current_state = 'game_loop'
                        
