
import math
from typing import Dict, Optional
import carla
from lib.InteractionUtils import InteractionUtils
from lib.LoggerFactory import LoggerFactory
from shapely.geometry import Polygon, LineString
from agents.pedestrians.planner.DynamicBehaviorModelFactory import DynamicBehaviorModelFactory
from agents.pedestrians.soft import BehaviorMatcher, Direction, NavPoint, GroupNavPath, NavPath
from agents.pedestrians.soft.LaneSection import LaneSection
from .NavPathModel import NavPathModel

from agents.pedestrians.soft.NavPath import NavPath
from ..PedestrianAgent import PedestrianAgent
from agents.pedestrians.factors import InternalFactors
from lib import Geometry, Utils, VehicleUtils
from .CrosswalkGeometry import CrosswalkGeometry
import numpy as np
from agents.pedestrians.destination.CrosswalkModel import CrosswalkModel


class NavPathModelWithGroups:
    """Every pedestrian will use this model instead of NavPathModel where there are groups. This model can form and break groups.
    """
    
    def __init__(
            groupNavPath: GroupNavPath,
            vehicleLagForInitialization = 10 # to let the vehicle pick up speed
        ):
        
        self.groupNavPath = groupNavPath

        self.debug = debug
        self.visualizer = agent.visualizer

        self.logger = LoggerFactory.create(f"NavPathModelWithGroup")


        self.vehicleLaneId = None # need this one to retranslate remaining nav points
        self.vehicleLag = vehicleLagForInitialization # we add a lag in distance to let the vehicle pick up the speed.

        self._agentToNavPath = {}
        self._navPathModels: List[NavPathModel] = []
    
    def register(agent, navPath: NavPath):
        self._agentToNavPath[agent] = navPath

    def unregister(agent):
        del self._agentToNavPath[agent]
    
    def getNavPathModel(agent):
        return self._agentToNavPath[agent]
    
    def generateNavPathModels():
        pass



        