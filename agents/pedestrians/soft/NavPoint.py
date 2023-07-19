from typing import List, Set
from agents.pedestrians.soft.BehaviorType import BehaviorType
from agents.pedestrians.soft.Direction import Direction
from agents.pedestrians.soft.LaneSection import LaneSection
from agents.pedestrians.soft.Side import Side
from dataclasses import dataclass, field


@dataclass
class NavPointLocation:
    laneId: int  #lane id wrt the ego vehicle's direction. ego vehicle has left and right vehicles, where ego's lane has id 0. left is negative, right is positive. sidewalks are lanes
    laneSection: LaneSection
    distanceToEgo: float # on the lane cooordinate system # distance can be negative
    distanceToInitialEgo: float # on the lane cooordinate system # distance can be negative

    pass

@dataclass
class NavPointBehavior:
    speed: float = None
    direction: Direction = None
    behaviorTags: Set[BehaviorType] = field(default_factory=set)



class NavPoint:
    """
    """
    def __init__(
            self, 
            location: NavPointLocation,
            behavior: NavPointBehavior
            ):
        
        # self.ttc = None

        self.location = location
        self.behavior = behavior

    def __str__(self) -> str:
        return (
            f"{self.laneId}: {self.laneSection}"
            f"\n{self.distanceToEgo}: {self.distanceToInitialEgo}"
            f"\nspeed: {self.speed}, direction: {self.direction}"
            f"\ntags: {self.behaviorTags}"
        )
    
    @property
    def laneId(self) -> int:
        return self.location.laneId
    
    @property
    def laneSection(self) -> LaneSection:
        return self.location.laneSection
    
    @property
    def distanceToEgo(self) -> float:
        return self.location.distanceToEgo
    
    @property
    def distanceToInitialEgo(self) -> float:
        return self.location.distanceToInitialEgo
    
    @property
    def speed(self) -> float:
        return self.behavior.speed
    
    @property
    def direction(self) -> Direction:
        return self.behavior.direction

    @property
    def behaviorTags(self) -> Set[BehaviorType]:
        return self.behavior.behaviorTags
    
    def addBehaviorTag(self, behaviorTag: BehaviorType):
        self.behaviorTags.add(behaviorTag)

    
    def isInFrontOfEgo(self):
        return self.distanceToEgo > 0
    def isBehindEgo(self):
        return self.distanceToEgo < 0

    def isOnEgosLeft(self):
        if self.laneId < 0:
            return True
        if self.laneId == 0:
            if self.laneSection == LaneSection.LEFT:
                return True
        return False
    
    def isOnEgosRight(self):
        if self.laneId > 0:
            return True
        if self.laneId == 0:
            if self.laneSection == LaneSection.RIGHT:
                return True
        return False
    
    def hasEvasiveFlinch(self):
        return BehaviorType.EVASIVE_FLINCH in self.behaviorTags
    def hasEvasiveSpeedup(self):
        return BehaviorType.EVASIVE_FLINCH in self.behaviorTags
    def hasEvasiveSlowdown(self):
        return BehaviorType.EVASIVE_FLINCH in self.behaviorTags
    def hasEvasiveStop(self):
        return BehaviorType.EVASIVE_FLINCH in self.behaviorTags
    
    def getOtherSide(self, other: 'NavPoint') -> LaneSection:
        """This is also in the ego's perspective

        Args:
            other (NavPoint): _description_

        Returns:
            _type_: _description_
        """

        if self.laneId > other.laneId: 
            return Side.LEFT
        elif self.laneId < other.laneId:
            return Side.RIGHT

        if self.laneId == other.laneId:
            if self.laneSection == LaneSection.LEFT:
                if other.laneSection == LaneSection.LEFT:
                    return Side.SAME
                else:
                    return Side.RIGHT
            elif self.laneSection == LaneSection.MIDDLE:
                if other.laneSection == LaneSection.MIDDLE:
                    return Side.SAME
                if other.laneSection == LaneSection.LEFT:
                    return Side.LEFT
                return Side.RIGHT
            
            elif self.laneSection == LaneSection.RIGHT:
                if other.laneSection == LaneSection.RIGHT:
                    return Side.SAME
                else:
                    return Side.LEFT
    
    def stepsToRightLane(self) -> int:
        if self.laneSection == LaneSection.MIDDLE:
            return 2
        if self.laneSection == LaneSection.LEFT:
            return 3
        return 1
    
    def stepsToLeftLane(self) -> int:
        if self.laneSection == LaneSection.MIDDLE:
            return 2
        if self.laneSection == LaneSection.RIGHT:
            return 3
        return 1
    
    def getStepsToOther(self, other: 'NavPoint') -> int:

        otherSide = self.getOtherSide(other)

        if otherSide == Side.SAME:
            return 0
        
        if self.laneId == other.laneId:
            # not in the same side
            if (self.laneSection == LaneSection.MIDDLE) or (other.laneSection == LaneSection.MIDDLE): # no matter where the other is, the steps will always be one
                return 1
            return 2 # on right or left
            
        
        middleLaneSteps = (abs(self.laneId - other.laneId) - 1) * 3
        # now we can assume the lanes are adjacent to each other
        if otherSide == Side.LEFT:
            myStepsToTheLeftLane = self.stepsToLeftLane()
            otherStepsToTheRightLane = other.stepsToRightLane()
            # print("myStepsToTheLeftLane", myStepsToTheLeftLane)
            # print("otherStepsToTheRightLane", otherStepsToTheRightLane)
            return myStepsToTheLeftLane + otherStepsToTheRightLane + middleLaneSteps - 1
        else:
            myStepsToTheRightLane = self.stepsToRightLane()
            otherStepsToTheLeftLane = other.stepsToLeftLane()
            # print("myStepsToTheRightLane", myStepsToTheRightLane)
            # print("otherStepsToTheLeftLane", otherStepsToTheLeftLane)
            return myStepsToTheRightLane + otherStepsToTheLeftLane + middleLaneSteps - 1
        
            
        


