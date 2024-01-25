from agents.pedestrians.BehaviorType import BehaviorType
from agents.pedestrians.soft.LaneSection import LaneSection
from agents.pedestrians.soft.NavPath import NavPath
from agents.pedestrians.soft.Side import Side


class BehaviorMatcherParams:
    def __init__(self):
        self._evasiveRetreat = {}
        self._evasiveFlinch = {}
        self._evasiveStop = {}
        self._evasiveSlowdownAndStop = {}
        self._evasiveSpeedup = {}
        self._evasiveSlowdown = {}
    
    @property
    def evasiveStop(self):
        defaultConfig = {
            "maxSpeed": 0.1
        }
        defaultConfig.update(self._evasiveStop)
        return defaultConfig
    
    @property
    def evasiveFlinch(self):
        defaultConfig = {
            "maxSpeedNext": 0.1,
            "yDistancePrevNext": 0.5,
            "maxStepsPrevNext": 1
        }
        defaultConfig.update(self._evasiveFlinch)
        return defaultConfig

    @property
    def evasiveRetreat(self):
        defaultConfig = {
            "minStepNext": 1,
            "yDistancePrevNext": 0.5,
        }
        defaultConfig.update(self._evasiveRetreat)
        return defaultConfig


class BehaviorMatcher:

    def __init__(self, params: BehaviorMatcherParams = None):
        """_summary_

        Args:
            greedy (bool, optional): If greedy behaviors will be tagged to start in previous nav points. If not greedy, behavior will be exactly tagged in the navpoint showing it. Both has their useage. Defaults to True.
        """
        if params is None:
            self.params = BehaviorMatcherParams()

    def tagNavPoints(self, navPath: NavPath):
        for idx, _ in enumerate(navPath.path):
            self.tagNavPoint(idx, navPath)
    
    def tagNavPoint(self, idx:int, navPath: NavPath):
        navPoint = navPath.path[idx]
        # if navPoint.isBehindEgo():
        #     return
        # print(f"{idx} checking")
        
        if self.showsEvasiveRetreat(idx, navPath):
            # print(f"{idx} showsEvasiveRetreat")
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_RETREAT)
        elif self.showsEvasiveFlinch(idx, navPath):
            # print(f"{idx} showsEvasiveFlinch")
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_FLINCH)
        elif self.showsEvasiveStop(idx, navPath):
            # print(f"{idx} showsEvasiveStop")
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_STOP)
        elif self.showsEvasiveSlowdownAndStop(idx, navPath):
            # print(f"{idx} showsEvasiveSlowdownAndStop")
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_SLOWDOWN_STOP)
        elif self.showsEvasiveSpeedup(idx, navPath):
            # print(f"{idx} showsEvasiveSpeedup")
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_SPEEDUP)
        elif self.showsEvasiveSlowdown(idx, navPath):
            # print(f"{idx} showsEvasiveSlowdown")
            navPoint.addBehaviorTag(BehaviorType.EVASIVE_SLOWDOWN)

    def showsEvasiveRetreat(self, idx:int, navPath: NavPath):
        """TODO
        1. y displacement threshold
        2. current one has to be on the same lane as the vehicle

        Args:
            idx (int): _description_
            navPath (NavPath): _description_

        Returns:
            _type_: _description_
        """
        navPoint = navPath.path[idx]
        if navPoint.isBehindEgo():
            return
        
        # means the next nav and the previous nav points are on the same side.
        if idx == 0 or idx == len(navPath.path) - 1: 
            return False
        
        prevNavPoint = navPath.path[idx - 1]
        previousPointSide = navPoint.getOtherSide(prevNavPoint)
            # TODO, we consider retreat if next navpoints are at least 2 steps away current
        for i in range(idx + 1, len(navPath.path)):
            nextNavPoint = navPath.path[i]
            if navPoint.getOtherSide(nextNavPoint) != previousPointSide:
                return False
            print("steps", navPoint.getStepsToOther(nextNavPoint))
            if navPoint.getStepsToOther(nextNavPoint) > 1:
                return True
        
        return False


    def showsEvasiveFlinch(self, idx:int, navPath: NavPath):
        # TODO:
        # 1. prev and next same lane and lane section
        # 2. speed threshold
        # 3. within 0.5 meters y axis.
        # 4. cur and next same within 1 step 
        # 5. We should search for suitable prev and next within the thresholds first.
        navPoint = navPath.path[idx]
        if navPoint.isBehindEgo():
            return
        
        # means the next nav and the previous nav points are on the same side.
        if idx == 0 or idx == len(navPath.path) - 1: 
            return False
        
        prevNavPoint = navPath.path[idx - 1]
        nextNavPoint = navPath.path[idx + 1]
        if navPoint.getOtherSide(prevNavPoint) == navPoint.getOtherSide(nextNavPoint):
            return True
        
        return False
    
    def showsEvasiveStop(self, idx:int, navPath: NavPath):
        navPoint = navPath.path[idx]
        if navPoint.isBehindEgo():
            return
        if navPoint.speed <= self.params.evasiveStop["maxSpeed"]: # need improvement
            return True
    
        # if idx == len(navPath.path) - 1:
        #     return False
        # nextNavPoint = navPath.path[idx + 1]
        # # if navPoint is on the left of the ego, the next point has to be on the right of the current
        # if navPoint.isOnEgosLeft():
        #     print(f"on ego's left")
        #     if navPoint.getOtherSide(nextNavPoint) == Side.SAME:
        #         return True
        # # if navPoint is on the right of the ego, the next point has to be on the left  of the current
        # if navPoint.isOnEgosRight():
        #     print(f"on ego's right")
        #     if navPoint.getOtherSide(nextNavPoint) == Side.SAME:
        #         return True
        

    def showsEvasiveSlowdownAndStop(self, idx:int, navPath: NavPath):
        """Pattern1: navPoint is on side of the vehicle, the pedestrian keeps moving and makes a stop on the same side of the vehicle and between the navpoint and the vehicle axis

        Args:
            idx (int): _description_
            navPath (NavPath): _description_

        Returns:
            _type_: _description_
        """
        navPoint = navPath.path[idx]
        if navPoint.isBehindEgo() or navPoint.laneId == 0:
            return
    
        if idx == len(navPath.path) - 1:
            return False
        
        allowedSides = set([Side.SAME])
        allowedLanes = []
        if navPoint.laneId < 0:
            allowedLanes = set(range(navPoint.laneId, 0))
        else:
            allowedLanes = set(range(1, navPoint.laneId + 1))

        if navPoint.isOnEgosLeft():
            allowedSides.add(Side.RIGHT)
        elif navPoint.isOnEgosRight():
            allowedSides.add(Side.LEFT)
        
        
        pointsInPattern = []
        for nextIdx in range(idx+1, len(navPath.path)):
            nextNavPoint = navPath.path[nextIdx]
            if nextNavPoint.laneId not in allowedLanes:
                break
            if navPoint.getOtherSide(nextNavPoint) not in allowedSides:
                break
            pointsInPattern.append(nextNavPoint)
        
        if len(pointsInPattern) > 1:
            lastNavPoint = pointsInPattern[-1]
            if lastNavPoint.speed <= 0.1:
                return True

        return False
        

    def showsEvasiveSpeedup(self, idx:int, navPath: NavPath):
        """
        1. Next nav point has to be in front of ego 
        2. Next nav must be on the vehicle lane
        3. The direction from the current and the next is the same as the pedestrian's crossing direction.

        Args:
            idx (int): _description_
            navPath (NavPath): _description_

        Returns:
            _type_: _description_
        """
        navPoint = navPath.path[idx]

        if navPoint.hasEvasiveFlinch() or navPoint.isBehindEgo() or  navPoint.speed is None:
            return False

        if idx == len(navPath.path) - 1:
            return False
        nextNavPoint = navPath.path[idx + 1]
        if nextNavPoint.isBehindEgo():
            return False
        if navPoint.speed < nextNavPoint.speed: 
            # TODO we need to consider the direction, too.
            # if navPoint is on the left of the ego, the next point has to be on the right
            if navPoint.isOnEgosLeft():
                if navPoint.getOtherSide(nextNavPoint) == Side.RIGHT: # TODO or center
                    return True
            # if navPoint is on the right of the ego, the next point has to be on the left
            if navPoint.isOnEgosRight():
                if navPoint.getOtherSide(nextNavPoint) == Side.LEFT: # TODO or center
                    return True
            
        return False

    def showsEvasiveSlowdown(self, idx:int, navPath: NavPath):
        navPoint = navPath.path[idx]

        if navPoint.hasEvasiveFlinch() or navPoint.isBehindEgo() or  navPoint.speed is None:
            return False
        
        
        if idx == len(navPath.path) - 1:
            return False
        nextNavPoint = navPath.path[idx + 1]
        if navPoint.speed > nextNavPoint.speed:

            # print(f"{idx} slowing down. has to be on the same side")
            return (navPoint.isOnEgosLeft() and nextNavPoint.isOnEgosLeft()) or (navPoint.isOnEgosRight() and nextNavPoint.isOnEgosRight())
        
            # # if navPoint is on the left of the ego, the next point has to be on the right of the current
            # if navPoint.isOnEgosLeft():
            #     # print(f"on ego's left")
            #     if navPoint.getOtherSide(nextNavPoint) == Side.RIGHT:
            #         return True
            # # if navPoint is on the right of the ego, the next point has to be on the left  of the current
            # if navPoint.isOnEgosRight():
            #     # print(f"on ego's right")
            #     if navPoint.getOtherSide(nextNavPoint) == Side.LEFT:
            #         return True
        return False