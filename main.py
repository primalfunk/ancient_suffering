import logging_config
import pygame
from title_screen import TitleScreen
from game_manager import GameManager


if __name__ == "__main__":
    logging_config.setup_logging()
    pygame.init()
    pygame.mixer.init()
    pygame.display.init()
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    screen = pygame.display.set_mode((1920, 1080)) #pygame.FULLSCREEN
    title_screen = TitleScreen(screen, screen_width, screen_height)
    game_manager = GameManager(screen, screen_width, screen_height)
    fade_in_done = False
    title_screen.init_music(0.75)
    current_state = "title_screen"
    while True:
        events = pygame.event.get()
        if current_state == "title_screen":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    print(f"Keydown event detected in main loop, sent to title_screen to handle")
                title_screen.handle_event(event)
                
            title_screen.update()
            if title_screen.is_finished:
                pygame.mixer.music.stop()
                game_manager.player.name = title_screen.player_name
                current_state = "fade_in"

        elif current_state == "fade_in" and not fade_in_done:
            fade_surface = pygame.Surface((screen_width, screen_height))
            fade_surface.fill((0, 0, 0))
            for alpha in range(255, -1, -5):
                game_manager.draw_initial_ui_onto_surface(screen)
                fade_surface.set_alpha(alpha)
                screen.blit(fade_surface, (0, 0))
                pygame.display.flip()
                pygame.time.delay(35)
            fade_in_done = True
            current_state = 'game_loop'
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.3)

        elif current_state == 'game_loop':
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_manager.toggle_fullscreen()
                    elif event.key == pygame.K_r:
                        game_manager.restart_game()
                    else:
                        game_manager.process_keypress(event)
                # Process other game loop specific events here
            if not game_manager.check_for_combat():
                game_manager.update()
                pygame.display.flip()
            else:
                current_state = 'combat'
                pygame.mixer.music.stop()
                game_manager.combat.init_music(volume=0.7)

        elif current_state == 'combat':
            game_manager.combat.update()
            game_manager.update()
            events = pygame.event.get()
            game_manager.ui.process_input(events)
            if game_manager.combat.is_over:
                pygame.mixer.music.stop()
                game_manager.ui.room_display.update_post_combat(screen)
                game_manager.combat.is_over = False
                game_manager.combat.resume_regular_music()
                current_state = 'game_loop'

pygame.quit()