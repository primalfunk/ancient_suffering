from game_manager import GameManager
import os
import pygame
from map import Map
import tkinter as tk

from title_screen import TitleScreen

if __name__ == "__main__":
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width, window_height = 1600, 900
    position_x = (screen_width - window_width) // 2
    position_y = (screen_height - window_height) // 2
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (position_x, position_y)

    pygame.init()
    screen = pygame.display.set_mode([1600, 900])  # Adjust as per your window size

    title_screen = TitleScreen(screen)
    title_screen.run()  # Run the title screen loop

    # blackout after title
    screen.fill((0, 0, 0))
    pygame.display.flip()
    pygame.time.wait(2000)

    game_map = Map(25)
    game_manager = GameManager(game_map, screen)
    game_manager.run_game_loop()  # Start the game loop