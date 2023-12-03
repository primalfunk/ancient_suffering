import random
import json

class Room:
    word_lists = None  # Class variable to store the original word lists

    @classmethod
    def load_words(cls, filename='words.json'):
        with open(filename, 'r') as file:
            cls.word_lists = json.load(file)

    def __init__(self, room_id, x, y):
        if not Room.word_lists:  # Load words if not already loaded
            Room.load_words()
        self.country = self._select_word(self.country)
        print(self.country)
        self.room_id = room_id
        self.x = x
        self.y = y
        self.name = ""
        self.connections = {'n': None, 's': None, 'e': None, 'w': None}
        self.lit = 0
        self.generate_name()

    def generate_name(self):
        adjective = self._select_word(self.adjectives)
        words = self._select_word(self.countries)
        self.name = " ".join(words)
        self.name = self.name.title()

    def _select_word(self, word_list):
        if not word_list:
            word_list.extend(Room.word_lists[word_list.name].copy())
        return word_list.pop(random.randrange(len(word_list)))

    def connect(self, direction, room):
        opposites = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
        self.connections[direction] = room
        room.connections[opposites[direction]] = self

for i in range(1, 10):
    room = Room(1, i, 0)
    print(room.name)