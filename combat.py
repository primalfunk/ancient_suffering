class Combat:
    def __init__(self, player):
        self.player = player
        self.enemy = self.player.current_room.enemy
        print(f"Initiating combat with {self.player.name} and {self.enemy.name}")