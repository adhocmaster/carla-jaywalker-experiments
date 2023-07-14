from typing import List

from agents.pedestrians.soft.NavPoint import NavPoint


class NavPath:

    def __init__(
            self, 
            roadWidth: float, 
            path: List[NavPoint], 
            nEgoDirectionLanes: int, 
            nEgoOppositeDirectionLanes: int,
            avgSpeed: float,
            maxSpeed: float,
            minSpeed: float,
            egoLaneWrtCenter: int
            ):
        self.roadWidth = roadWidth
        self.path = path
        self.nEgoDirectionLanes = nEgoDirectionLanes
        self.nEgoOppositeDirectionLanes = nEgoOppositeDirectionLanes
        self.avgSpeed = avgSpeed
        self.maxSpeed = maxSpeed
        self.minSpeed = minSpeed
        assert egoLaneWrtCenter > 0
        self.egoLaneWrtCenter = egoLaneWrtCenter

    @property
    def nLanes(self):
        return self.nEgoDirectionLanes + self.nEgoOppositeDirectionLanes

    @property
    def laneWidth(self):
        return self.roadWidth / (self.nLanes)
    
    
    @property
    def roadLength(self):
        maxDistanceToEgo = 0
        for navPoint in self.path:
            maxDistanceToEgo = max(maxDistanceToEgo, navPoint.distanceToEgo)
        return maxDistanceToEgo * 1.5


    
