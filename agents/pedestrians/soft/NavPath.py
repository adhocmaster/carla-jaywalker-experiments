from typing import List

from dataclasses import dataclass, field

from agents.pedestrians.soft.NavPoint import NavPoint

@dataclass
class NavPathRoadConfiguration:
    roadWidth: float
    nEgoDirectionLanes: int
    nEgoOppositeDirectionLanes: int

@dataclass
class NavPathEgoConfiguration:
    avgSpeed: float
    maxSpeed: float
    minSpeed: float
    egoLaneWrtCenter: int
    egoSpeedStart: float
    egoSpeedEnd: float

class NavPath:

    def __init__(
            self, 
            roadConfiguration: NavPathRoadConfiguration,
            egoConfiguration: NavPathEgoConfiguration,
            path: List[NavPoint], 
            ):
        
        self.roadConfiguration = roadConfiguration
        self.egoConfiguration = egoConfiguration
        self.path = path
        
        # self.nEgoDirectionLanes = nEgoDirectionLanes
        # self.nEgoOppositeDirectionLanes = nEgoOppositeDirectionLanes
        # self.avgSpeed = avgSpeed
        # self.maxSpeed = maxSpeed
        # self.minSpeed = minSpeed

        assert egoConfiguration.egoLaneWrtCenter > 0
        # self.egoLaneWrtCenter = egoLaneWrtCenter
        # self.egoSpeedStart = egoSpeedStart
        # self.egoSpeedEnd = egoSpeedEnd

    @property
    def roadWidth(self):
        return self.roadConfiguration.roadWidth
    
    
    @property
    def nEgoDirectionLanes(self):
        return self.roadConfiguration.nEgoDirectionLanes
    
    
    @property
    def nEgoOppositeDirectionLanes(self):
        return self.roadConfiguration.nEgoOppositeDirectionLanes
    
    
    @property
    def avgSpeed(self):
        return self.egoConfiguration.avgSpeed
    
    
    @property
    def maxSpeed(self):
        return self.egoConfiguration.maxSpeed
    
    
    @property
    def minSpeed(self):
        return self.egoConfiguration.minSpeed
    
    
    @property
    def egoLaneWrtCenter(self):
        return self.egoConfiguration.egoLaneWrtCenter
    
    
    @property
    def egoSpeedStart(self):
        return self.egoConfiguration.egoSpeedStart
    
    
    @property
    def egoSpeedEnd(self):
        return self.egoConfiguration.egoSpeedEnd

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
    
    def getPointLaneIdWrtCenter(self, point: NavPoint) -> int:
        return self.egoLaneWrtCenter + point.laneId

    
