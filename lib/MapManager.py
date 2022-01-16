from re import X
from turtle import distance
import carla
import math
from enum import Enum
from .ClientUser import ClientUser

class MapNames(Enum):
    circle_t_junctions = 'circle_t_junctions'
    t_junction = 't_junction'


class MapManager(ClientUser):

    def __init__(self, client):
        super().__init__(client)
        self.currentMapName = None

    @property
    def spawn_points(self):
        return self.map.get_spawn_points()
    
    def load(self, mapName: MapNames):
        self.client.load_world(mapName.value)

        self.currentMapName = mapName

        self.configureSpectator()




    def configureSpectator(self):

        (x, y, z) = self.getSpectatorPos()
        print(f"setting spectator position to ({x}, {y}, {z})")
        transform = carla.Transform(carla.Location(x=x, y=y, z=z), carla.Rotation(pitch=-90)) 
        # if self.currentMapName == MapNames.circle_t_junctions:
        #     transform = carla.Transform(carla.Location(x=x, y=y, z=z), carla.Rotation(pitch=-90)) 
        # elif self.currentMapName == MapNames.t_junction:
        #     transform = carla.Transform(carla.Location(x=x, y=y, z=z), carla.Rotation(pitch=-90)) 
        # else:
        #     transform = carla.Transform(carla.Location(x=x, y=y, z=z*3), carla.Rotation(pitch=-90)) 

        
        spectator = self.world.get_spectator()
        spectator.set_transform(transform)
        # spectator.set_transform(carla.Transform(carla.Location(x=-120, y=0, z=100), carla.Rotation(pitch=-90)))

    
    def getSpectatorPos(self):
        minX = 9999999
        maxX = -9999999
        minY = 9999999
        maxY = -9999999

        
        waypoints = self.map.generate_waypoints(distance=5.0)

        # for point in self.spawn_points:
        for point in waypoints:
            location = point.transform.location
            x = location.x
            y = location.y
            # print(f"point: ({x}, {y})" )

            if x < minX:
                minX = x
            if x > maxX:
                maxX = x
            if y < minY:
                minY = y
            if y > maxY:
                maxY = y


        diag = math.sqrt((minX - maxX)**2 + (minY - maxY)**2)
        print(f"Map bb: ({minX}, {minY}) ({maxX, maxY})" )
        print(f"Map bb diag: ({diag})" )

        return ((minX + maxX) / 2, (minY + maxY) / 2, diag)
            
