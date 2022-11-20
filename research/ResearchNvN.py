from genericpath import sameopenfile
from turtle import distance
import carla
import logging
import random
import os
import numpy as np
from datetime import date

from .BaseResearch import BaseResearch
from settings.circular_t_junction_settings import circular_t_junction_settings
from settings.town02_settings import town02_settings
from settings import SettingsManager
from agents.pedestrians import PedestrianFactory
from agents.pedestrians.factors import Factors
from agents.vehicles import VehicleFactory
from lib import Simulator, EpisodeSimulator, SimulationMode
from lib import Utils
import pandas as pd
from lib.MapManager import MapNames

class ResearchNvN(BaseResearch):
    
    def __init__(self, client: carla.Client, 
                 mapName=MapNames.circle_t_junctions, 
                 logLevel="INFO", 
                 outputDir:str = "logs", 
                 simulationMode = SimulationMode.ASYNCHRONOUS,
                 settingsId = "setting1",
                 stats=False):

        self.name = "Research1v1"

        super().__init__(name=self.name, 
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
        self.settingsManager = SettingsManager(self.client, settings)


        self.pedFactory = PedestrianFactory(self.client, visualizer=self.visualizer, time_delta=self.time_delta)
        self.vehicleFactory = VehicleFactory(self.client, visualizer=self.visualizer)

        self.episodeNumber = 0
        self.episodeTimeStep = 0
        self.stats = stats
        self.settingsId = settingsId

        self.optionalFactors = [Factors.DRUNKEN_WALKER]
        # self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE]
        # self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE, Factors.SURVIVAL_DESTINATION]
        # self.optionalFactors = [Factors.ANTISURVIVAL]
        # self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE, Factors.SURVIVAL_DESTINATION]
        # self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE, Factors.SURVIVAL_DESTINATION, Factors.DRUNKEN_WALKER]
        # self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE, Factors.DRUNKEN_WALKER]
        # self.optionalFactors = []

        # self.optionalFactors = [Factors.SURVIVAL_DESTINATION, Factors.DRUNKEN_WALKER, Factors.FREEZING_FACTOR]

#        self.optionalFactors = [Factors.SURVIVAL_DESTINATION, Factors.FREEZING_FACTOR]


        self.setup()