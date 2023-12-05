class Inventory:
    def __init__(self, max_size=5):
        self.items = []
        self.max_size = max_size
        self.full = False

    def add_item(self, item):
        if len(self.items) < self.max_size:
            self.items.append(item)
            return True
        else:
            self.full = True
            return False

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            return True
        else:
            if len(self.items) < self.max_size:
                self.full = False
            return False

    def has_item(self, item):
        return item in self.items

    def get_items(self):
        return self.items