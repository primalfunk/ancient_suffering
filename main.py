from map import Map
from game_manager import GameManager

if __name__ == "__main__":
    game_map = Map(30)
    game_manager = GameManager(game_map)
    game_manager.run_game_loop()