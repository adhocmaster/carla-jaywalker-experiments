from turtle import color
import carla
import numpy as np
import random
import math

from .LoggerFactory import LoggerFactory
from .ClientUser import ClientUser
from .MapManager import MapManager

class SimulationVisualization(ClientUser):

    def __init__(self, client: carla.Client, mapManager: MapManager):
        self.name = "SimulationVisualization"
        super().__init__(client)

        self.logger = LoggerFactory.create(self.name)

        self.mapManager = mapManager
        # self.pool = eventlet.GreenPool()

        self.tracking = {} # actor id -> tracking config

        # self.pool.spawn_n(self.world.on_tick, self.onTick)
        # self.world.on_tick(self.onTick) # freezes. may need greenlets.

    

    def onTick(self, world_snapshot):
        for actorId in self.tracking:
            actor_snapshot = world_snapshot.find(actorId)
            if actor_snapshot is not None:
                life_time = self.tracking[actorId]["life_time"]
                color = self.tracking[actorId]["color"]
                self.drawWalkerBB(actor_snapshot, color=color, life_time=life_time)

    #region unit functions

    def getRandomColor(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        a = random.randint(0, 100)

        return (r, g, b, a)

    
    def drawPoint(self, location, size=0.1, color=(255,0,0,100), life_time = 0):
        self.debug.draw_point(location, size, carla.Color(*color),  life_time)

    def drawBox(self, bb, rotation, thickness=0.1, color=(255,0,0, 100), life_time = 0):
        self.debug.draw_box(
                    bb,
                    rotation, 
                    thickness, 
                    carla.Color(*color),
                    life_time)

    def drawTextOnMap(self, location, text, life_time=600):
        self.drawText(
            location=location, 
            text=text, 
            draw_shadow = True,
            color=(0, 0, 0),
            life_time=life_time
        )

    def drawText(self, location, text, draw_shadow=False, color=(255,0,0), life_time=600):
        """[summary]

        Args:
            location ([type]): [description]
            text ([type]): [description]
            draw_shadow (bool, optional): [description]. Defaults to False.
            color (tuple, optional): [description]. Defaults to (255,0,0).
            life_time (float, optional): [description]. > 1. 0 or -1 has no effect.
        """
        self.debug.draw_string(
            location, 
            text, 
            draw_shadow,
            carla.Color(*color),
            life_time
            )

        # self.debug.draw_string(
        #     location, 
        #     "Where is my text", 
        #     False,
        #     carla.Color(0, 0, 0, 0),
        #     life_time
        #     )



    
    
    def draw00(self):
        bb = carla.BoundingBox(
            carla.Location(x=0, y=0, z=0), 
            carla.Vector3D(1,1,1) # assuming all walkers are less than 2 meters in height
        )
        rotation = carla.Rotation(pitch=-90)
        self.drawBox(bb, rotation, thickness=0.1, color=(0, 0, 0, 0))

    def drawWalkerBB(self, walker, thickness=0.1, color=(255,0,0, 100), life_time = 0):
        bb = self.getWalkerBB(walker)
        rotation = walker.get_transform().rotation
        self.drawBox(bb, rotation, thickness=thickness, color=color, life_time=life_time)

    def getWalkerBB(self, walker):
        return carla.BoundingBox(
            walker.get_transform().location, 
            carla.Vector3D(0.5,0.5,2) # assuming all walkers are less than 2 meters in height
        )

    # trajectory

    def trackOnTick(self, actorId, config=None):
        if config is None:
            config = { 'life_time': 0 }

        if 'color' not in config:
            config['color'] = self.getRandomColor()

        self.tracking[actorId] = config
    

    # some positional information

    def drawWalkerNavigationPoints(self, navPoints):
        for point in navPoints:
            location = point.location
            self.logger.debug(f"walker spawn position ({location.x}, {location.y})")
            self.drawPoint(location=location, size=0.05, color=(0, 255, 0))
            self.drawTextOnMap(location=carla.Location(location.x, location.y, 1), text=f"({round(location.x)}, {round(location.y)})")

    def drawSpawnPoints(self):
        spawn_points = self.map.get_spawn_points()
        for point in spawn_points:
            location = point.location
            self.logger.debug(f"spawn_point position ({location.x}, {location.y})")
            self.drawPoint(location=location, size=0.05)
            self.drawTextOnMap(location=carla.Location(location.x, location.y, 1), text=f"({round(location.x)}, {round(location.y)})")


    def drawSpectatorPoint(self):
        spectator = self.world.get_spectator()
        location = spectator.get_location()
        self.logger.debug(f"spectator position ({location.x}, {location.y}, {location.z})")
        drawLocation = carla.Location(location.x, location.y, 0)
        self.drawPoint(location=drawLocation, size=0.1, color=(0, 50, 200))
        self.drawTextOnMap(location=carla.Location(location.x, location.y, 10), text=f"Center ({round(location.x)}, {round(location.y)})")

        
    def drawWaypoints(self, waypoints, z=0.5, life_time=1.0):
        """
        Draw a list of waypoints at a certain height given in z.

            :param world: carla.world object
            :param waypoints: list or iterable container with the waypoints to draw
            :param z: height in meters
        """
        for wpt in waypoints:
            wpt_t = wpt.transform
            begin = wpt_t.location + carla.Location(z=z)
            angle = math.radians(wpt_t.rotation.yaw)
            end = begin + carla.Location(x=math.cos(angle), y=math.sin(angle))
            self.world.debug.draw_arrow(
                begin, 
                end, 
                arrow_size=0.3, 
                color=carla.Color(25, 25, 25), 
                life_time=life_time
                )


    def drawDirection(self, location, direction, z=0.5, life_time=1.0):
        """
        Draw a list of waypoints at a certain height given in z.

            :param world: carla.world object
            :param waypoints: list or iterable container with the waypoints to draw
            :param z: height in meters
        """
        begin = location + carla.Location(z=z)
        angle = math.atan2(direction.y, direction.x)
        end = begin + carla.Location(x=math.cos(angle), y=math.sin(angle))
        self.world.debug.draw_arrow(
            begin, 
            end, 
            arrow_size=0.3, 
            color=carla.Color(50, 25, 25), 
            life_time=life_time
            )
    def drawAllWaypoints(self, z=0.5, life_time=1.0):
        """
        Draw a list of waypoints at a certain height given in z.

            :param world: carla.world object
            :param waypoints: list or iterable container with the waypoints to draw
            :param z: height in meters
        """
        self.drawWaypoints(self.mapManager.waypoints, life_time=life_time)



    def drawDestinationPoint(self, location, life_time=20.0):
        self.logger.debug(f"destinationSpawnPoint position ({location.x}, {location.y})")
        overlayLocation = carla.Location(location.x, location.y, 10)
        self.drawPoint(location=overlayLocation, size=0.1, color=(0, 255, 0), life_time=life_time)
        self.drawTextOnMap(location=overlayLocation, text=f"dest", life_time=life_time)



    

    
