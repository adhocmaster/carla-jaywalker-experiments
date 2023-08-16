
import random
from agents.pedestrians.soft import *
from research.Research1v1 import Research1v1


class Research1v1NavPathModel(Research1v1):
    
    
    @property
    def navPath(self):
        if hasattr(self, "_navPath") is False or self._navPath is None:
            navPaths = self.settingsManager.getNavPaths("settings/nav_path_straight_road.json")
            self._navPath = random.choice(navPaths)
            self._navPath = navPaths[1] # just for testing

        return self._navPath
    
    def createWalker(self):
        
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
