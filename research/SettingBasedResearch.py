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

class SettingBasedResearch(BaseResearch):
    
    def __init__(self, 
                 name:str,
                 client: carla.Client, 
                 mapName=MapNames.circle_t_junctions, 
                 logLevel="INFO", 
                 outputDir:str = "logs", 
                 simulationMode = SimulationMode.ASYNCHRONOUS,
                 settingsId = "setting1",
                 stats=False,
                 maxStepsPerCrossing=200):


        super().__init__(name=name, 
                         client=client, 
                         mapName=mapName, 
                         logLevel=logLevel, 
                         outputDir=outputDir,
                         simulationMode=simulationMode)

        settings = None
        if mapName == MapNames.circle_t_junctions:
            settings = circular_t_junction_settings
        elif mapName == MapNames.Town02_Opt:
            settings = town02_settings
        elif mapName == MapNames.Town03_Opt:
            settings = town03_settings
        elif mapName == MapNames.varied_width_lanes:
            settings = varied_width_lanes_settings
        else:
            raise Exception(f"Map {mapName} is missing settings")
        self.settingsManager = SettingsManager(self.client, settings)

        self.pedFactory = PedestrianFactory(self.client, visualizer=self.visualizer, time_delta=self.time_delta)
        self.vehicleFactory = VehicleFactory(self.client, visualizer=self.visualizer)

        self.episodeNumber = 0
        self.episodeTimeStep = 0
        self.stats = stats
        self.maxStepsPerCrossing = maxStepsPerCrossing
        self.settingsId = settingsId
    
    pass



    def setup(self):

        
        # self.settingsManager.load("setting3")
        # return 
        self.settingsManager.load(self.settingsId)

        self.simulator = None # populated when run

        # change spectator if in setting
        spectatorSettings = self.settingsManager.getSpectatorSettings()
        if spectatorSettings is not None:
            self.mapManager.setSpectator(spectatorSettings)

    def reset(self):
        super().reset()
        spectatorSettings = self.settingsManager.getSpectatorSettings()
        if spectatorSettings is not None:
            self.mapManager.setSpectator(spectatorSettings)