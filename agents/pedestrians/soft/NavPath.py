from typing import List

from agents.pedestrians.soft.NavPoint import NavPoint


class NavPath:

    def __init__(self, roadWidth: float, path: List[NavPoint]):
        self._path = path
        self._roadWidth = roadWidth
        self._nEgoDirectionLanes = 0
        self._nEgoOppositeDirectionLanes = 0
    
