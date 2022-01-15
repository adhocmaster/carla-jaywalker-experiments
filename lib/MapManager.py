import carla
from enum import Enum
from .ClientUser import ClientUser

class MapNames(Enum):
    circle_t_junctions = 'circle_t_junctions'
    t_junction = 't_junction'
    default_t_junction = 'default_t_junction'


class MapManager(ClientUser):

    def __init__(self, client):
        super().__init__(client)
        self.currentMapName = None

    
    def load(self, mapName: MapNames):
        self.client.load_world(mapName.value)

        self.refreshClient()

        self.currentMapName = mapName

        self.configureSpectator()


    def configureSpectator(self):
        if self.currentMapName == MapNames.circle_t_junctions:
            transform = carla.Transform(carla.Location(x=-120, y=0, z=100), carla.Rotation(pitch=-90)) 
        else:
            transform = carla.Transform(carla.Location(x=-120, y=0, z=150), carla.Rotation(pitch=-90)) 

        
        spectator = self.world.get_spectator()
        spectator.set_transform(transform)