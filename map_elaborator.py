import json
from region_assignment import RegionAssignment
from room_decoration import RoomDecoration
from object_distribution import ObjectDistribution

class MapElaborator:
    def __init__(self, map_instance, words_file):
        self.map = map_instance
        with open(words_file, 'r') as file:
            data = json.load(file)
        self.region_assignment = RegionAssignment(self.map, data['locations'])
        self.region_assignment.assign_regions()

        self.room_decoration = RoomDecoration(self.map, data)
        self.room_decoration.decorate_rooms()

        self.object_distribution = ObjectDistribution(self.map)
        self.object_distribution.distribute_items()