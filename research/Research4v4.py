from genericpath import sameopenfile
from turtle import distance
import carla
import logging
import random
import os
import numpy as np
import json
from datetime import date

from agents.pedestrians.soft import Direction, LaneSection, NavPath, NavPoint
from research.SettingBasedResearch import SettingBasedResearch

from .BaseResearch import BaseResearch
from settings.circular_t_junction_settings import circular_t_junction_settings
from settings.town02_settings import town02_settings
from settings.town03_settings import town03_settings
from settings.varied_width_lanes_settings import varied_width_lanes_settings
from settings import SettingsManager
from agents.pedestrians import PedestrianFactory
from agents.pedestrians.factors import Factors
from agents.vehicles import VehicleFactory
from lib import Simulator, EpisodeSimulator, SimulationMode, EpisodeTrajectoryRecorder, ActorClass
from lib import Utils
import pandas as pd
from lib.MapManager import MapNames
from agents.pedestrians.soft import NavPointLocation, NavPointBehavior, LaneSection, Direction, NavPath

class Research4v4(SettingBasedResearch):
    
    def __init__(self, 
                 client: carla.Client, 
                 mapName=MapNames.circle_t_junctions, 
                 logLevel="INFO", 
                 outputDir:str = "logs", 
                 simulationMode = SimulationMode.ASYNCHRONOUS,
                 settingsId = "setting1",
                 stats=False,
                 maxStepsPerCrossing=200
                 ):

        self.name = "Research4v4"

        super().__init__(name=self.name, 
                         client=client, 
                         mapName=mapName, 
                         logLevel=logLevel, 
                         outputDir=outputDir,
                         simulationMode=simulationMode,
                         settingsId=settingsId,
                         stats=stats,
                         maxStepsPerCrossing=maxStepsPerCrossing
                         )

        self.setup()

    def setup(self):
        super().setup()

        
    @property
    def navPath(self):
        if self._navPath is None:
            point1 = NavPoint(
                NavPointLocation(
                    laneId=-1,
                    laneSection=LaneSection.LEFT,
                    distanceToEgo=24.0, 
                    distanceToInitialEgo=24.0, 
                ),
                NavPointBehavior(
                    speed=1,
                    direction=Direction.LR
                )
            )

            point2 = NavPoint(
                NavPointLocation(
                    laneId=-1,
                    laneSection=LaneSection.MIDDLE,
                    distanceToEgo=7.0, 
                    distanceToInitialEgo=25.0, 
                ),
                NavPointBehavior(
                    speed=0.5,
                    direction=Direction.LR
                )
            )

            point3 = NavPoint(
                NavPointLocation(
                    laneId=-1,
                    laneSection=LaneSection.MIDDLE,
                    distanceToEgo=1.0, 
                    distanceToInitialEgo=25.0, 
                ),
                NavPointBehavior(
                    speed=0.1,
                    direction=Direction.LR
                )
            )


            point4 = NavPoint(
                NavPointLocation(
                    laneId=0,
                    laneSection=LaneSection.LEFT,
                    distanceToEgo=-1, 
                    distanceToInitialEgo=25.0, 
                ),
                NavPointBehavior(
                    speed=1,
                    direction=Direction.LR
                )
            )

            self._navPath = NavPath(
                roadWidth=2 * 3.5,
                path=[point1, point2, point3, point4],
                nEgoDirectionLanes=1,
                nEgoOppositeDirectionLanes=1,
                avgSpeed=0.5,
                maxSpeed=1.5,
                minSpeed=0.0,
                egoLaneWrtCenter = 1,
                egoSpeedStart=20,
                egoSpeedEnd=10
            )
        return self._navPath
    
    def createDynamicAgents(self):
        
        self.createVehicle()
        
        self.tickOrWaitBeforeSimulation() # otherwise we can get wrong vehicle location!
        self.createWalker()
        pass

    def recreateDynamicAgents(self):
        # 1. recreated vehicle
        self.recreateVehicle()
        self.tickOrWaitBeforeSimulation() # otherwise we can get wrong vehicle location!

        # 2. reset walker
        self.resetWalker(sameOrigin=True)
        self.walkerAgent.setEgoVehicle(self.vehicle)

        pass
