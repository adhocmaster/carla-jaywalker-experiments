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
            minSpeed: float
            ):
        self.roadWidth = roadWidth
        self.path = path
        self.nEgoDirectionLanes = nEgoDirectionLanes
        self.nEgoOppositeDirectionLanes = nEgoOppositeDirectionLanes
        self.avgSpeed = avgSpeed
        self.maxSpeed = maxSpeed
        self.minSpeed = minSpeed
        

    
