import carla
import numpy as np
import random

class SimulationVisualization:

    def __init__(self, client):
        self.client = client
        self.world = client.get_world()
        self.map = self.world.get_map()
        self.debug = self.world.debug

        self.tracking = {} # actor id -> tracking config

        self.world.on_tick(self.onTick)

    

    def onTick(self, world_snapshot):
        for actorId in self.tracking:
            actor_snapshot = world_snapshot.find(actorId)
            if actor_snapshot is not None:
                lifetime = self.tracking[actorId]["lifetime"]
                color = self.tracking[actorId]["color"]
                self.drawWalkerBB(actor_snapshot, color=color, lifetime=lifetime)

    #region unit functions

    def getRandomColor(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        a = random.randint(0, 100)

        return (r, g, b, a)

    def drawBox(self, bb, rotation, thickness=0.1, color=(255,0,0, 100), lifetime = 0):
        self.debug.draw_box(
                    bb,
                    rotation, 
                    thickness, 
                    carla.Color(*color),
                    lifetime)
    
    def draw00(self):
        bb = carla.BoundingBox(
            carla.Location(x=0, y=0, z=0), 
            carla.Vector3D(1,1,1) # assuming all walkers are less than 2 meters in height
        )
        rotation = carla.Rotation(pitch=-90)
        self.drawBox(bb, rotation, thickness=1, color=(0, 0, 0, 0))

    def drawWalkerBB(self, walker, thickness=0.1, color=(255,0,0, 100), lifetime = 0):
        bb = self.getWalkerBB(walker)
        rotation = walker.get_transform().rotation
        self.drawBox(bb, rotation, thickness=thickness, color=color, lifetime=lifetime)

    def getWalkerBB(self, walker):
        return carla.BoundingBox(
            walker.get_transform().location, 
            carla.Vector3D(0.5,0.5,2) # assuming all walkers are less than 2 meters in height
        )

    # trajectory

    def trackOnTick(self, actorId, config=None):
        if config is None:
            config = { 'lifetime': 0 }

        if 'color' not in config:
            config['color'] = self.getRandomColor()

        self.tracking[actorId] = config
    


    

    
