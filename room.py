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
        self.room_id = room_id
        self.x = x
        self.y = y
        self.name = ""
        self.connections = {'n': None, 's': None, 'e': None, 'w': None}
        self.lit = 0
        # Copy word lists for this instance
        self.adjectives = Room.word_lists['adjectives'].copy()
        self.nouns = Room.word_lists['nouns'].copy()
        self.adverbs = Room.word_lists['adverbs'].copy()
        self.verbs = Room.word_lists['verbs'].copy()

    def generate_name(self):
        adjective = self._select_word(self.adjectives)
        noun = self._select_word(self.nouns)
        adverb = self._select_word(self.adverbs)
        verb = self._select_word(self.verbs)
        words = [adjective, adverb, noun, verb]
        result = []
        for word in words:
            word = word.lower()
            result.append(word)
        random.shuffle(result)
        self.name = " ".join(result)

    def _select_word(self, word_list):
        if not word_list:
            word_list.extend(Room.word_lists[word_list.name].copy())
        return word_list.pop(random.randrange(len(word_list)))

    def connect(self, direction, room):
        opposites = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
        self.connections[direction] = room
        room.connections[opposites[direction]] = self

# Example Usage
for i in range(1, 10):
    room1 = Room(i, 0, 0)
    room1.generate_name()
    print(f"Room Name: {room1.name}")