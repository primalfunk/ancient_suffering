import json
import logging
from region_assignment import RegionAssignment
from room_decoration import RoomDecoration
from object_distribution import ObjectDistribution
# Configure logging
logging.basicConfig(filename='map.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class MapElaborator:
    def __init__(self, map_instance, words_file):
        self.map = map_instance
        logging.debug("MapElaborator captured the map. Assigning regions...")
        with open(words_file, 'r') as file:
            data = json.load(file)
        self.region_assignment = RegionAssignment(self.map, data['locations'])
        logging.debug("Regions assigned, decorating rooms...")
        self.region_assignment.assign_regions()

        self.object_distribution = ObjectDistribution(self.map)
        logging.debug("Objects distributed.")
        self.object_distribution.distribute_items()

        self.room_decoration = RoomDecoration(self.map, data)
        logging.debug("Rooms decorated, distributing objects...")
        self.room_decoration.decorate_rooms()