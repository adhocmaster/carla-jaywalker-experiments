import logging
import random
from typing import List

import carla
from agents.pedestrians.factors import *
from agents.pedestrians.factors import InternalFactors
from agents.pedestrians.PedestrianAgent import PedestrianAgent
from agents.pedestrians.planner.SingleOncomingVehicleLocalPlanner import \
    SingleOncomingVehicleLocalPlanner
from lib import (ActorManager, ClientUser, LoggerFactory, ObstacleManager,
                 SimulationMode)


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

    
    def spawn(self, spawnPoint: carla.Transform):
        walkerBp = self.create()
        # walkerBp.set_attribute('is_invincible', 'true')  
        walker = self.world.spawn_actor(walkerBp, spawnPoint)

        self.walkers.append(walker)
        return walker
    
    def spawnWithCollision(self, spawnPoint: carla.Transform):
        walker = self.spawn(spawnPoint)
        collision = self.addCollisonSensor(walker)
        return walker, collision

    def addCollisonSensor(self, walker: carla.Walker):

        if walker not in PedestrianFactory.collisionSensors:
            spawnPoint = carla.Transform(location = carla.Location(0, 0, 1))
            PedestrianFactory.collisionSensors[walker] = self.world.spawn_actor(self.collisionBp, spawnPoint, attach_to=walker)

        return PedestrianFactory.collisionSensors[walker]

    
    def addObstacleDetector(self, walker: carla.Walker):
        if walker not in PedestrianFactory.obstacleDetectors:
            spawnPoint = carla.Transform(location = carla.Location(0, 0, 1))
            PedestrianFactory.obstacleDetectors[walker] = self.world.spawn_actor(self.obstacleBp, spawnPoint, attach_to=walker)

        return PedestrianFactory.obstacleDetectors[walker]

    def batchSpawnWalkerAndAgent(self,

            spawnPoints: List[carla.Transform],
            logLevel=logging.INFO, 
            internalFactorsPath = None, 
            optionalFactors: List[Factors] = None,
            config=None,
            simulationMode = SimulationMode.ASYNCHRONOUS

        ):

        # 1. batch spawn walkers
        # 2. wait for tick or tick
        # 3. batch spawn agents

        walkers = self.batchSpawnWalkers(spawnPoints)
        if simulationMode == SimulationMode.ASYNCHRONOUS:
            self.world.wait_for_tick()
        else:
            self.world.tick()
        
        agents = self.batchCreateAgents(
            walkers,
            logLevel=logLevel, 
            internalFactorsPath = internalFactorsPath, 
            optionalFactors = optionalFactors,
            config=config,
        )

        return walkers, agents

       
    def batchSpawnWalkers(self, spawnPoints: List[carla.Transform]):
        
        batch = []
        for spawnPoint in spawnPoints:
            if spawnPoint.location.z < 0.5:
                spawnPoint.location.z = 0.5 

                walkerBp = self.create()
                
                batch.append(carla.command.SpawnActor(walkerBp, spawnPoint))
        
        generatedWalkers = []

        for response in self.client.apply_batch_sync(batch):
            if response.error:
                logging.error(response.error)
            else:
                walker = self.world.get_actor(response.actor_id)
                generatedWalkers.append(walker)
                self.walkers.extend(generatedWalkers)
        
        return generatedWalkers

    
    def batchCreateAgents(
            self, 
            walkers: List[carla.Walker], 
            logLevel=logging.INFO, 
            internalFactorsPath = None, 
            optionalFactors: List[Factors] = None,
            config=None
        ) -> List[PedestrianAgent]:

        agents = []
        for walker in walkers:
            agents.append(
                self.createAgent(
                    walker=walker,
                    logLevel=logLevel,
                    internalFactorsPath=internalFactorsPath,
                    optionalFactors=optionalFactors,
                    config=config
                )
            )
        
        return agents


    
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

        self.addPlanners(agent, internalFactorsPath=internalFactorsPath, optionalFactors=optionalFactors, logLevel=logLevel)
        # self.initSensors(agent)
        
        return agent

    def addPlanners(self, agent: PedestrianAgent, internalFactorsPath = None, optionalFactors: List[Factors] = None, logLevel=logging.INFO):
        
        actorManager = ActorManager(agent.walker, time_delta=self.time_delta)
        obstacleManager = ObstacleManager(agent.walker, time_delta=self.time_delta)

        if internalFactorsPath is None:
            self.logger.warn(f"Internation factor path is None. Using the default at ({PedestrianFactory.internalFactorPath})")
            internalFactorsPath = PedestrianFactory.internalFactorPath
        
        internalFactors = InternalFactors(internalFactorsPath)


        localPlanner = SingleOncomingVehicleLocalPlanner(agent, actorManager=actorManager, obstacleManager=obstacleManager, internalFactors=internalFactors, time_delta=self.time_delta, logLevel=logLevel)

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


    
