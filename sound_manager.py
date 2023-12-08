import pygame

class SoundManager:
    def __init__(self):
        self.sounds = {
            "win": pygame.mixer.Sound('sounds/applause.wav'),
            "arcane": pygame.mixer.Sound('sounds/arcane.wav'),
            "round": pygame.mixer.Sound('sounds/attack_round.wav'),
            "danger": pygame.mixer.Sound('sounds/enemysighted.wav'),
            "inventory": pygame.mixer.Sound('sounds/found_something_nice.wav'),
            "gameover": pygame.mixer.Sound('sounds/gameover.wav'),
            "travel": pygame.mixer.Sound('sounds/movement.wav'),
            "notification": pygame.mixer.Sound('sounds/notif.wav')
        }

    def play_sound(self, sound_name, volume):
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play()
        else:
            print(f"Sound '{sound_name}' not found.")