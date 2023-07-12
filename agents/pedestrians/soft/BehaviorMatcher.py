from agents.pedestrians.soft.BehaviorType import BehaviorType
from agents.pedestrians.soft.NavPath import NavPath
from agents.pedestrians.soft.Side import Side


class BehaviorMatcher:

    def tagNavPoints(self, navPath: NavPath):
        for idx, _ in enumerate(navPath.path):
            self.tagNavPoint(idx, navPath)
    
    def tagNavPoint(self, idx:int, navPath: NavPath):
        navPoint = navPath.path[idx]
        if self.showsEvasiveStop(idx, navPath):
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_STOP)
        elif self.showsEvasiveRetreat(idx, navPath):
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_RETREAT)
        elif self.showsEvasiveFlinch(idx, navPath):
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_FLINCH)
        elif self.showsEvasiveSpeedup(idx, navPath):
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_SPEEDUP)
        elif self.showsEvasiveSlowdown(idx, navPath):
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_SLOWDOWN)

    def showsEvasiveStop(self, idx:int, navPath: NavPath):
        navPoint = navPath.path[idx]
        if navPoint.speed < 0.1 and navPoint.distanceToEgo >= 0: # need improvement
            return True
        
    def showsEvasiveRetreat(self, idx:int, navPath: NavPath):
        navPoint = navPath.path[idx]
        
        if navPoint.hasEvasiveStop():
            return False

        # means the next nav and the previous nav points are on the same side.
        if idx == 0 or idx == len(navPath.path) - 1: 
            return False
        
        prevNavPoint = navPath.path[idx - 1]
        nextNavPoint = navPath.path[idx + 1]
        if navPoint.getOtherSide(prevNavPoint) == navPoint.getOtherSide(nextNavPoint):
            # TODO, we consider retreat if next navpoints are at least half length wide
            for i in range(1, len(navPath.path)):
                pass
            return True
        
        return False


    def showsEvasiveFlinch(self, idx:int, navPath: NavPath):
        navPoint = navPath.path[idx]
        
        if navPoint.hasEvasiveStop():
            return False

        # means the next nav and the previous nav points are on the same side.
        if idx == 0 or idx == len(navPath.path) - 1: 
            return False
        
        prevNavPoint = navPath.path[idx - 1]
        nextNavPoint = navPath.path[idx + 1]
        if navPoint.getOtherSide(prevNavPoint) == navPoint.getOtherSide(nextNavPoint):
            return True
        
        return False

    def showsEvasiveSpeedup(self, idx:int, navPath: NavPath):
        navPoint = navPath.path[idx]

        if navPoint.hasEvasiveFlinch():
            return False

        if idx == len(navPath.path) - 1:
            return False
        nextNavPoint = navPath.path[idx + 1]
        if navPoint.speed < nextNavPoint.speed: # we need to consider the direction, too.
            # if navPoint is on the left of the ego, the next point has to be on the right
            if navPoint.isOnEgosLeft():
                if navPoint.getOtherSide(nextNavPoint) == Side.RIGHT:
                    return True
            # if navPoint is on the right of the ego, the next point has to be on the left
            if navPoint.isOnEgosRight():
                if navPoint.getOtherSide(nextNavPoint) == Side.LEFT:
                    return True
            
        return False

    def showsEvasiveSlowdown(self, idx:int, navPath: NavPath):
        navPoint = navPath.path[idx]

        if navPoint.hasEvasiveFlinch():
            return False
        
        if idx == len(navPath.path) - 1:
            return False
        nextNavPoint = navPath.path[idx + 1]
        if navPoint.speed > nextNavPoint.speed:
        
            # if navPoint is on the left of the ego, the next point has to be on the right
            if navPoint.isOnEgosLeft():
                if navPoint.getOtherSide(nextNavPoint) == Side.RIGHT:
                    return True
            # if navPoint is on the right of the ego, the next point has to be on the left
            if navPoint.isOnEgosRight():
                if navPoint.getOtherSide(nextNavPoint) == Side.LEFT:
                    return True
        return False