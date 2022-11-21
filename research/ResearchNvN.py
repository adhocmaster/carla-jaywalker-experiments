from genericpath import sameopenfile
from turtle import distance
import carla
import logging
import random
import os
import numpy as np
from datetime import date

from .BaseResearch import BaseResearch
from settings.circular_t_junction_settings import circular_t_junction_settings
from settings.town02_settings import town02_settings
from settings import SettingsManager
from agents.pedestrians import PedestrianFactory
from agents.pedestrians.factors import Factors
from agents.vehicles import VehicleFactory
from lib import Simulator, EpisodeSimulator, SimulationMode, RoadHelper, Utils
import pandas as pd
from lib.MapManager import MapNames

class ResearchNvN(BaseResearch):

    """
        There is no episodic behavior in this research. Vehicles and Walkers are created randomly and are destroyed when they reach their destinations.
        So, we save their trajectories in a single dataframe with frame numbers.
    """
    
    def __init__(self, client: carla.Client, 
                 mapName=MapNames.circle_t_junctions, 
                 logLevel="INFO", 
                 outputDir:str = "logs", 
                 simulationMode = SimulationMode.ASYNCHRONOUS,
                 settingsId = None,
                 stats=False,
                 maxNVehicles = 10,
                 maxNPedestrians = 10
                 ):

        self.name = "ResearchNvN"

        super().__init__(name=self.name, 
                         client=client, 
                         mapName=mapName, 
                         logLevel=logLevel, 
                         outputDir=outputDir,
                         simulationMode=simulationMode)

        settings = None
        if mapName == MapNames.circle_t_junctions:
            settings = circular_t_junction_settings
        elif mapName == MapNames.Town02_Opt:
            settings = town02_settings
        self.settingsManager = SettingsManager(self.client, settings)


        self.pedFactory = PedestrianFactory(self.client, visualizer=self.visualizer, time_delta=self.time_delta)
        self.vehicleFactory = VehicleFactory(self.client, visualizer=self.visualizer)

        self.episodeNumber = 0
        self.episodeTimeStep = 0
        self.stats = stats
        self.settingsId = settingsId

        self.maxNVehicles = maxNVehicles
        self.maxNPedestrians = maxNPedestrians

        self.setup()
        

    def setup(self):
        # self.settingsManager.load("setting3")
        # return 
        if self.settingsId is not None:
            self.settingsManager.load(self.settingsId)

        # self.walker = None
        # self.walkerAgent = None
        # self.walkerSetting = self.getWalkerSetting()
        # self.walkerSpawnPoint = carla.Transform(location = self.walkerSetting.source)
        # self.walkerDestination = self.walkerSetting.destination

        # self.vehicle = None
        # self.vehicleAgent = None
        # self.vehicleSetting = self.getVehicleSetting()
        # self.vehicleSpawnPoint = self.settingsManager.locationToVehicleSpawnPoint(self.vehicleSetting.source)
        # self.vehicleDestination = self.vehicleSetting.destination

        self.simulator = None # populated when run

        self.statDataframe = pd.DataFrame()
        self.initStatDict()
    
    def initStatDict(self):
        # TODO 
        pass
    
    def reset(self):
        """Does not reset episode number. Only used for episodic simulator
        """
        raise Exception(f"reset not implemented")
        # self.logger.info(f"Resetting environment")
        # self.pedFactory.reset()
        # self.vehicleFactory.reset()

        # super().reset()

        # self.episodeTimeStep = 0
        # self.createDynamicAgents()
        # self.setupSimulator(episodic=True)

        
    
    def createDynamicAgents(self):
        
        # TODO pass

        nVtoCreate = self.maxNVehicles - self.vehicleFactory.size()
        nPToCreate = self.maxNPedestrians - self.pedFactory.size()
       
        pass

    def createVehicles(self, n):
        """We randomly generate some vehicles in map creator's suggested spawn points
            or in the vicinity of an existing vehicle

        Args:
            n (_type_): _description_
        """
        randomSplit = n // 2
        spawnPoints = random.sample(self.world.get_spawn_points(), randomSplit)
        generatedVehicles = self.vehicleFactory.batchSpawn(spawnPoints, autoPilot=True)

        self.tickOrWaitBeforeSimulation() # otherwise we can get wrong vehicle location!

        vicinitySplit = n - len(generatedVehicles)

    
    def createVehiclesNear(self, n, existingVehicle: carla.Vehicle = None):
        
        if existingVehicle is None:
            existingVehicle = random.choice(self.vehicleFactory.getVehicles())
        
        if existingVehicle is None:
            self.logger.warn(f"No vehicle in the simulation. Cannot spawn nearby vehicles")

        nearbyWps = RoadHelper.getWaypointsNearVehicle(self.map, existingVehicle):

        if n > len(nearbyWps):
            raise Exception(f"cannot create more vehicles than available way points"

        chosenWps = random.sample(nearbyWps, n)

        # TODO

        



    def setupSimulator(self, episodic=False):
        """Must be called after all actors are created.

        Args:
            episodic (bool, optional): _description_. Defaults to False.
        """
        self.episodeNumber = 1 # updated when resetted

        onTickers = [self.visualizer.onTick, self.onTick] # onTick must be called before restart
        onEnders = [self.onEnd]

        if episodic:
            terminalSignalers = []
            self.simulator = EpisodeSimulator(self.client, terminalSignalers=terminalSignalers, onTickers=onTickers, onEnders=onEnders, simulationMode=self.simulationMode)
        else:
            # onTickers.append(self.restart)
            self.simulator = Simulator(self.client, onTickers=onTickers, onEnders=onEnders, simulationMode=self.simulationMode)
        
    
    def runAsync(self, maxTicks=1000):
        """Runs in asynchronous mode only

        Args:
            maxTicks (int, optional): _description_. Defaults to 1000.
        """
            

        try:
            assert self.simulationMode == SimulationMode.ASYNCHRONOUS
            self.createDynamicAgents()
            
            # self.world.wait_for_tick()
            self.tickOrWaitBeforeSimulation()

            self.setupSimulator(False)

            self.simulator.run(maxTicks)
        except Exception as e:
            self.logger.exception(e)
            self.destoryActors()

    
    
    def onEnd(self):
        self.destoryActors()
        self.saveStats()

    def onTick(self, world_snapshot):

        self.episodeTimeStep += 1

        self.collectStats(world_snapshot)

        # self.walkerAgent.onTickStart(world_snapshot)

        # self.updateWalker(world_snapshot)
        # self.updateVehicle(world_snapshot)

        # # draw waypoints upto walker

        # walkerWp = self.map.get_waypoint(self.walkerAgent.location).transform.location
        # waypoints = Utils.getWaypointsToDestination(self.vehicle, walkerWp)
        # self.visualizer.drawWaypoints(waypoints, color=(0, 0, 0), z=1, life_time=0.1)
        # self.logger.info(f"Linear distance to pedestrian {self.walkerAgent.actorManager.distanceFromNearestOncomingVehicle()}")
        # self.logger.info(f"Arc distance to pedestrian {Utils.getDistanceCoveredByWaypoints(waypoints)}")

    
    
    def collectStats(self, world_snapshot):
        if not self.stats:
            return
        
        # TODO:
        pass
    
    def saveStats(self):
        if not self.stats:
            return

        dateStr = date.today().strftime("%Y-%m-%d-%H-%M")
        statsPath = os.path.join(self.outputDir, f"{self.name}-{dateStr}-trajectories.csv")
        # df = pd.DataFrame.from_dict(self.statDict)
        # df.to_csv(statsPath, index=False)

        if len(self.statDataframe) == 0:
            self.logger.warn("Empty stats. It means no episode was completed in this run")
            return
        self.statDataframe.to_csv(statsPath, index=False)
        pass