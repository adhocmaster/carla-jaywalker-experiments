import numpy as np
import random
import carla
from agents.pedestrians.soft import *
from lib import SimulationMode
from lib.MapManager import MapNames
from research.Research1v1 import Research1v1


class Research1v1NavPathModel(Research1v1):
    
    
    def __init__(self, 
                 client: carla.Client, 
                 mapName=MapNames.circle_t_junctions, 
                 logLevel="INFO", 
                 outputDir:str = "logs", 
                 simulationMode = SimulationMode.ASYNCHRONOUS,
                 settingsId = "setting1",
                 stats=False,
                 record=False,
                 ignoreStatsSteps=0,
                 maxStepsPerCrossing=200,
                 navPathFilePath="data/navpath/nav_path_straight_road.json",
                 scenario = "psi-0002",
                 ):

        super().__init__(
                         client=client, 
                         mapName=mapName, 
                         logLevel=logLevel, 
                         outputDir=outputDir,
                         simulationMode=simulationMode,
                         settingsId=settingsId,
                         stats=stats,
                         ignoreStatsSteps=ignoreStatsSteps,
                         record=record,
                         maxStepsPerCrossing=maxStepsPerCrossing
                         )
        
        self.name = "Research1v1NavPathModel"

        self.scenario = scenario
        self.navPathFilePath = navPathFilePath
        pass
        
    @property
    def navPath(self) -> NavPath:
        if hasattr(self, "_navPath") is False or self._navPath is None:
            # navPaths = self.settingsManager.getNavPaths("data/navpath/nav_path_straight_road.json")
            # self._navPath = random.choice(navPaths)
            # self._navPath = navPaths[4] # just for testing
            
            self._navPath = self.settingsManager.getNavPath(self.navPathFilePath, self.scenario)[0]

        return self._navPath
    
    def createWalker(self):
        
        self.optionalFactors = []
        
        reverse = False
        if self.navPath.direction == Direction.RL:
            reverse = True

        super().createWalker(reverse=reverse)

        self.walkerAgent.setEgoVehicle(self.vehicle)
        self.walkerAgent.setNavPath(self.navPath)
        pass

    
    def resetWalker(self, sameOrigin=True):
        super().resetWalker(sameOrigin=True) # must always be same origin for nav points
        
        self.walkerAgent.setEgoVehicle(self.vehicle)
        self.walkerAgent.setNavPath(self.navPath)
        pass

    
    def createVehicle(self, randomizeSpawnPoint=False):
        
        # meanSpeed = (self.navPath.egoConfiguration.egoSpeedStart + self.navPath.egoConfiguration.egoSpeedEnd) / 2
        # sd = 0.1
        # maxSpeed = np.random.normal(meanSpeed, sd) 
        maxSpeed = np.random.uniform(self.navPath.egoConfiguration.egoSpeedStart, self.navPath.egoConfiguration.egoSpeedEnd)
        self.vehicle, self.vehicleAgent = super(Research1v1, self).createVehicle(self.getVehicleSetting(), maxSpeed=maxSpeed, randomizeSpawnPoint=randomizeSpawnPoint)