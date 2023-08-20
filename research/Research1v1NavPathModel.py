import numpy as np
import random
from agents.pedestrians.soft import *
from research.Research1v1 import Research1v1


class Research1v1NavPathModel(Research1v1):
    
    
    @property
    def navPath(self) -> NavPath:
        if hasattr(self, "_navPath") is False or self._navPath is None:
            navPaths = self.settingsManager.getNavPaths("settings/nav_path_straight_road.json")
            self._navPath = random.choice(navPaths)
            self._navPath = navPaths[3] # just for testing

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
        
        meanSpeed = (self.navPath.egoConfiguration.egoSpeedStart + self.navPath.egoConfiguration.egoSpeedEnd) / 2
        sd = 0.1
        maxSpeed = np.random.normal(meanSpeed, sd) 
        self.vehicle, self.vehicleAgent = super(Research1v1, self).createVehicle(self.getVehicleSetting(), maxSpeed=maxSpeed, randomizeSpawnPoint=randomizeSpawnPoint)