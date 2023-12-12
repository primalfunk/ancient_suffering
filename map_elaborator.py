import json
import logging
from region_assignment import RegionAssignment
from room_atmos import RoomAtmos
from room_decoration import RoomDecoration
from object_distribution import ObjectDistribution

class MapElaborator:
    def __init__(self, map_instance, words_file):
        self.map_logger = logging.getLogger('map')
        self.map = map_instance
        self.map_logger .debug("MapElaborator captured the map. Assigning regions...")
        with open(words_file, 'r') as file:
            data = json.load(file)
        self.region_assignment = RegionAssignment(self.map, data['locations'])
        self.map_logger.debug("Regions assigned, decorating rooms...")
        self.region_assignment.assign_regions()

        self.object_distribution = ObjectDistribution(self.map)
        self.map_logger .debug("Objects distributed.")
        self.object_distribution.distribute_items()

        self.room_decoration = RoomDecoration(self.map, data)
        self.map_logger.debug("Rooms decorated, distributing objects...")
        self.room_decoration.decorate_rooms()

        self.room_atmos = RoomAtmos(self.map, data)
        self.map_logger.debug("Objects distributed, adding atmosphere...")
        self.room_atmos.create_atmosphere()