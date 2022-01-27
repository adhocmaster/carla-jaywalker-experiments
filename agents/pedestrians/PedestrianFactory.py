import carla
import random
import logging

from agents.pedestrians.PedestrianAgent import PedestrianAgent
from agents.pedestrians.SingleOncomingVehicleLocalPlanner import SingleOncomingVehicleLocalPlanner
from lib import LoggerFactory

class PedestrianFactory:


    walkers = []
    collisionSensors = {}
    obstacleDetectors = {}

    def __init__(self, world, time_delta=0.1, visualizer=None):
        
        self.name = "PedestrianFactory"
        self.logger = LoggerFactory.create(self.name)

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

    
    def createAgent(self, walker: carla.Walker, desired_speed=1.5, logLevel=logging.INFO) -> PedestrianAgent:
        agent = PedestrianAgent(
            walker, 
            desired_speed=desired_speed,
            visualizer=self.visualizer, 
            time_delta=self.time_delta, 
            config={"LOG_LEVEL": logLevel}
            )

        self.addPlanners(agent)
        # self.initSensors(agent)
        
        return agent

    def addPlanners(self, agent: PedestrianAgent):
        localPlanner = SingleOncomingVehicleLocalPlanner()
        agent.setLocalPlanner(localPlanner)
        pass


    def initSensors(self, agent: PedestrianAgent):
        self.logger.info(f"{self.name}: adding sensors")
        # self.logger.info(f"{self.name}: adding collision detector")
        # agent.collisionSensor = pedFactor.addCollisonSensor(self._walker)
        # agent.collisionSensor.listen(lambda data: agent.handleWalkerCollision(data))

        # agent.obstacleDetector = pedFactor.addObstacleDetector(self.walker)
        # agent.obstacleDetector.listen(lambda data: agent.handWalkerObstacles(data))


    
