import pygame
from map import Map
from game_manager import GameManager
from title_screen import TitleScreen

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode([800, 600])  # Adjust as per your window size

    title_screen = TitleScreen(screen)
    title_screen.run()  # Run the title screen loop

    game_map = Map(25)
    game_manager = GameManager(game_map, screen)
    game_manager.run_game_loop()  # Start the game loop