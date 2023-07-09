from agents.pedestrians.soft.BehaviorType import BehaviorType
from agents.pedestrians.soft.NavPath import NavPath


class BehaviorMatcher:

    def tagNavPoints(self, navPath: NavPath):
        for idx, _ in enumerate(navPath.path):
            self.tagNavPoint(idx, navPath)
    
    def tagNavPoint(self, idx:int, navPath: NavPath):
        navPoint = navPath.path[idx]
        if self.showsEvasiveStop(idx, navPath):
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_STOP)
        if self.showsEvasiveFlinch(idx, navPath):
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_FLINCH)
        if self.showsEvasiveSpeedup(idx, navPath):
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_SPEEDUP)
        if self.showsEvasiveSlowdown(idx, navPath):
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_SLOWDOWN)

    def showsEvasiveStop(idx:int, navPath: NavPath):
        navPoint = navPath.path[idx]
        if navPoint.speed < 0.1 and navPoint.distanceToEgo >= 0: # need improvement
            return True
        
    def showsEvasiveFlinch(idx:int, navPath: NavPath):
        navPoint = navPath.path[idx]
        # means the next nav and the previous nav points are on the same side.
        if idx == 0 or idx == len(navPoint.path) - 1: 
            return False
        
        prevNavPoint = navPath.path[idx - 1]
        nextNavPoint = navPoint.path[idx + 1]
        if navPoint.getOtherSide(prevNavPoint) == navPoint.getOtherSide(nextNavPoint):
            return True
        
        return False


    def showsEvasiveSpeedup(idx:int, navPath: NavPath):
        navPoint = navPath.path[idx]
        if idx == len(navPoint.path) - 1:
            return False
        nextNavPoint = navPoint.path[idx + 1]
        if navPoint.speed < nextNavPoint.speed:
            return True
        
        return False

    def showsEvasiveSlowdown(idx:int, navPath: NavPath):
        navPoint = navPath.path[idx]
        if idx == len(navPoint.path) - 1:
            return False
        nextNavPoint = navPoint.path[idx + 1]
        if navPoint.speed > nextNavPoint.speed:
            return True
        
        return False