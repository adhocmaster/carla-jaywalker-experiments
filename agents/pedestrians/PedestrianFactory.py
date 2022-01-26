import carla
import random

from agents.pedestrians.PedestrianAgent import PedestrianAgent
from charset_normalizer import logging

class PedestrianFactory:

    walkers = []
    collisionSensors = {}
    obstacleDetectors = {}

    def __init__(self, world, time_delta=0.1, visualizer=None):
        self.world = world
        self.visualizer = visualizer
        self.time_delta = time_delta
        self.bpLib = self.world.get_blueprint_library()
        self.pedBps = self.bpLib.filter('walker.pedestrian.*')
        self.collisionBp = self.bpLib.find('sensor.other.collision')
        self.obstacleBp = self.bpLib.find('sensor.other.obstacle')
        self.obstacleBp.set_attribute('distance', '5')
        self.obstacleBp.set_attribute('hit_radius', '0.1')
        # self.obstacleBp.set_attribute('debug_linetrace', 'true')

    def create(self):
        walkerBp = random.choice(self.pedBps)
        return walkerBp
    
    def spawn(self, spawnPoint):
        walkerBp = self.create()
        # walkerBp.set_attribute('is_invincible', 'true')  
        walker = self.world.spawn_actor(walkerBp, spawnPoint)
        PedestrianFactory.walkers.append(walker)
        return walker
    
    def spawnWithCollision(self, spawnPoint):
        walker = self.spawn(spawnPoint)
        collision = self.addCollisonSensor(walker)
        return walker, collision

    def addCollisonSensor(self, walker):

        if walker not in PedestrianFactory.collisionSensors:
            spawnPoint = carla.Transform(location = carla.Location(0, 0, 1))
            PedestrianFactory.collisionSensors[walker] = self.world.spawn_actor(self.collisionBp, spawnPoint, attach_to=walker)

        return PedestrianFactory.collisionSensors[walker]

    
    def addObstacleDetector(self, walker):
        if walker not in PedestrianFactory.obstacleDetectors:
            spawnPoint = carla.Transform(location = carla.Location(0, 0, 1))
            PedestrianFactory.obstacleDetectors[walker] = self.world.spawn_actor(self.obstacleBp, spawnPoint, attach_to=walker)

        return PedestrianFactory.obstacleDetectors[walker]

    
    def createAgent(self, walker: carla.Walker, desired_speed=1.5, logLevel=logging.INFO):
        return PedestrianAgent(
            walker, 
            desired_speed=desired_speed,
            visualizer=self.visualizer, 
            time_delta=self.time_delta, 
            config={"LOG_LEVEL": logLevel}
            )



    
