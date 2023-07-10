from typing import List, Set
from agents.pedestrians.soft.BehaviorType import BehaviorType
from agents.pedestrians.soft.LaneSection import LaneSection
from agents.pedestrians.soft.Side import Side


class NavPoint:
    """
    """
    def __init__(
            self, 
            laneId: int, 
            laneSection: LaneSection, 
            distanceToEgo: float,
            speed: float,
            ):
        self.laneId = laneId #lane id wrt the ego vehicle's direction. ego vehicle has left and right vehicles, where ego's lane has id 0. left is negative, right is positive. sidewalks are lanes
        self.laneSection = laneSection
        self.distanceToEgo = distanceToEgo # on the lane cooordinate system # distance can be negative
        self.speed = speed 
        self.behaviorTags: Set[BehaviorType] = set([])
        # self.ttc = None
    
    def addBehaviorTag(self, behaviorTag: BehaviorType):
        self.behaviorTags.add(behaviorTag)
    
    def getOtherSide(self, other: 'NavPoint'):
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
        


