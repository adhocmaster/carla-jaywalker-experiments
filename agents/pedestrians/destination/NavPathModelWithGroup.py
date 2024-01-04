
import math
from typing import Dict, Optional
import carla
from lib.InteractionUtils import InteractionUtils
from lib.LoggerFactory import LoggerFactory
from shapely.geometry import Polygon, LineString
from agents.pedestrians.planner.DynamicBehaviorModelFactory import DynamicBehaviorModelFactory
from agents.pedestrians.soft import BehaviorMatcher, Direction, NavPoint
from agents.pedestrians.soft.LaneSection import LaneSection

from agents.pedestrians.soft.NavPath import NavPath
from ..PedestrianAgent import PedestrianAgent
from agents.pedestrians.factors import InternalFactors
from lib import Geometry, Utils, VehicleUtils
from .CrosswalkGeometry import CrosswalkGeometry
import numpy as np
from agents.pedestrians.destination.CrosswalkModel import CrosswalkModel


class NavPathModelWithGroup():
    
    def __init__(
            navPathModels: List[NavPathModel],
            vehicleLagForInitialization = 10 # to let the vehicle pick up speed
        ):
        
        self.navPathModels = navPathModels

        self.debug = debug
        self.visualizer = agent.visualizer

        self.logger = LoggerFactory.create(f"NavPathModelWithGroup")


        self.vehicleLaneId = None # need this one to retranslate remaining nav points
        self.vehicleLag = vehicleLagForInitialization # we add a lag in distance to let the vehicle pick up the speed.
        