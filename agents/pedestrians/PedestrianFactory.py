import carla
import random
import logging

from agents.pedestrians.PedestrianAgent import PedestrianAgent
from agents.pedestrians.planner.SingleOncomingVehicleLocalPlanner import SingleOncomingVehicleLocalPlanner
from agents.pedestrians.factors import InternalFactors
from lib import LoggerFactory, ClientUser
from lib.ActorManager import ActorManager
from lib.ObstacleManager import ObstacleManager
from typing import List
from agents.pedestrians.factors import *


class PedestrianFactory(ClientUser):

    internalFactorPath = "settings/internal_factors_default.yaml"

    walkers = []
    collisionSensors = {}
    obstacleDetectors = {}

    def __init__(self, client: carla.Client, time_delta, visualizer=None):
        
        self.name = "PedestrianFactory"
        self.logger = LoggerFactory.create(self.name)
        super().__init__(client)

        
        self.walkers = []
        self.collisionSensors = {}
        self.obstacleDetectors = {}

        self.visualizer = visualizer
        self.time_delta = time_delta

        self.bpLib = self.world.get_blueprint_library()
        self.pedBps = self.bpLib.filter('walker.pedestrian.*')
        self.collisionBp = self.bpLib.find('sensor.other.collision')
        self.obstacleBp = self.bpLib.find('sensor.other.obstacle')
        self.obstacleBp.set_attribute('distance', '5')
        self.obstacleBp.set_attribute('hit_radius', '0.1')
        # self.obstacleBp.set_attribute('debug_linetrace', 'true')

    
    def getWalkers(self):
        return self.walkers

    def create(self):
        walkerBp = random.choice(self.pedBps)
        return walkerBp

    
    def destroy(self, walker: carla.Walker):
        self.walkers.remove(walker)
        walker.destroy()


    def reset(self):
        for walker in self.walkers:
            self.destroy(walker)

    
    def spawn(self, spawnPoint):
        walkerBp = self.create()
        # walkerBp.set_attribute('is_invincible', 'true')  
        walker = self.world.spawn_actor(walkerBp, spawnPoint)

        self.walkers.append(walker)
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

    
    def createAgent(
        self, 
        walker: carla.Walker, 
        logLevel=logging.INFO, 
        internalFactorsPath = None, 
        optionalFactors: List[Factors] = None,
        config=None
        ) -> PedestrianAgent:

        if config is None:
            config = {}
        config["LOG_LEVEL"] = logLevel

        agent = PedestrianAgent(
            walker, 
            visualizer=self.visualizer, 
            time_delta=self.time_delta, 
            config=config
            )

        self.addPlanners(agent, internalFactorsPath=internalFactorsPath, optionalFactors=optionalFactors)
        # self.initSensors(agent)
        
        return agent

    def addPlanners(self, agent: PedestrianAgent, internalFactorsPath = None, optionalFactors: List[Factors] = None):
        
        actorManager = ActorManager(agent.walker, time_delta=self.time_delta)
        obstacleManager = ObstacleManager(agent.walker, time_delta=self.time_delta)

        if internalFactorsPath is None:
            self.logger.warn(f"Internation factor path is None. Using the default at ({PedestrianFactory.internalFactorPath})")
            internalFactorsPath = PedestrianFactory.internalFactorPath
        
        internalFactors = InternalFactors(internalFactorsPath)


        localPlanner = SingleOncomingVehicleLocalPlanner(agent, actorManager=actorManager, obstacleManager=obstacleManager, internalFactors=internalFactors, time_delta=self.time_delta)

        if optionalFactors is not None:
            localPlanner.createOptionalModels(optionalFactors=optionalFactors)
            
        agent.setLocalPlanner(localPlanner)

        
        pass


    def initSensors(self, agent: PedestrianAgent):
        self.logger.info(f"{self.name}: adding sensors")
        # self.logger.info(f"{self.name}: adding collision detector")
        # agent.collisionSensor = pedFactor.addCollisonSensor(self._walker)
        # agent.collisionSensor.listen(lambda data: agent.handleWalkerCollision(data))

        # agent.obstacleDetector = pedFactor.addObstacleDetector(self.walker)
        # agent.obstacleDetector.listen(lambda data: agent.handWalkerObstacles(data))


    
