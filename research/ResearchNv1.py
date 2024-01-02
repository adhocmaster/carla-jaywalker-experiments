from abc import abstractmethod
from genericpath import sameopenfile
from turtle import distance
from typing import Dict
import carla
import logging
import random
import os
import numpy as np
import json
from datetime import date
from typing import *

from agents.pedestrians.soft import Direction, LaneSection, NavPath, NavPoint
from research.SettingBasedResearch import SettingBasedResearch
from settings.SourceDestinationPair import SourceDestinationPair

from .BaseResearch import BaseResearch
from .ResearchActors import WalkerActor
from settings.circular_t_junction_settings import circular_t_junction_settings
from settings.town02_settings import town02_settings
from settings.town03_settings import town03_settings
from settings.varied_width_lanes_settings import varied_width_lanes_settings
from settings import SettingsManager
from agents.pedestrians import PedestrianFactory
from agents.pedestrians.factors import Factors
from agents.vehicles import VehicleFactory
from lib import Simulator, EpisodeSimulator, SimulationMode, ActorClass
from lib import Utils
from analysis.EpisodeTrajectoryRecorder import EpisodeTrajectoryRecorder
import pandas as pd
from lib.MapManager import MapNames
from agents.pedestrians.soft import NavPointLocation, NavPointBehavior, LaneSection, Direction, NavPath

class ResearchNv1(SettingBasedResearch):
    
    def __init__(self, 
                 client: carla.Client, 
                 mapName=MapNames.circle_t_junctions, 
                 logLevel="INFO", 
                 outputDir:str = "logs", 
                 simulationMode = SimulationMode.ASYNCHRONOUS,
                 settingsId = "setting1",
                 stats=False,
                 ignoreStatsSteps=0,
                 record=False,
                 maxStepsPerCrossing=200
                 ):

        self.name = "Research1v1"

        super().__init__(name=self.name, 
                         client=client, 
                         mapName=mapName, 
                         logLevel=logLevel, 
                         outputDir=outputDir,
                         simulationMode=simulationMode,
                         settingsId=settingsId,
                         stats=stats,
                         ignoreStatsSteps=ignoreStatsSteps,
                         record=record,
                         maxStepsPerCrossing=maxStepsPerCrossing
                         )

        self.optionalFactors = []
        # self.optionalFactors = [Factors.EVASIVE_RETREAT]
        # self.optionalFactors = [Factors.DRUNKEN_WALKER]
        # self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE]
        # self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE, Factors.EVASIVE_RETREAT]
        # self.optionalFactors = [Factors.ANTISURVIVAL]
        # self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE, Factors.EVASIVE_RETREAT]
        # self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE, Factors.EVASIVE_RETREAT, Factors.DRUNKEN_WALKER]
        # self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE, Factors.DRUNKEN_WALKER]

        # self.optionalFactors = [Factors.EVASIVE_RETREAT, Factors.DRUNKEN_WALKER, Factors.FREEZING_FACTOR]

#        self.optionalFactors = [Factors.EVASIVE_RETREAT, Factors.FREEZING_FACTOR]
        # self.optionalFactors = [Factors.EVASIVE_RETREAT, Factors.FREEZING_FACTOR, Factors.CROSSING_ON_COMING_VEHICLE]
        # self.dataCollector = DataCollector() # todo, create the meta
        self.setup()

    #region getters
    def getVehicle(self):
        return self.vehicle

    def getVehicleAgent(self):
        return self.vehicleAgent
    
    def getWalkers(self) -> List[WalkerActor]:
        return self.walkerActors
    

    

    #endregion

    def destoryActors(self):
        
        self.logger.info('\ndestroying  walkers')
        self.pedFactory.reset()
        self.logger.info('\ndestroying  vehicles')
        self.vehicleFactory.reset()
        # self.logger.info('\ndestroying  walkers')
        # if self.walker is not None:
        #     # self.walker.destroy()
        #     self.pedFactory.destroy(self.walker)

        # self.logger.info('\ndestroying  vehicles')
        # if self.vehicle is not None:
        #     self.vehicleFactory.destroy(self.vehicle)

    
    def setMap(self, mapName:MapNames):
        raise Exception('map cannot be changed for a research setting')



    def setup(self):


        super().setup()

        self.walkerActors: List[WalkerActor] = []

    

        self.vehicle = None
        self.vehicleAgent = None
        self.vehicleSetting = self.getVehicleSetting()
        self.vehicleSpawnPoint = self.settingsManager.locationToVehicleSpawnPoint(self.vehicleSetting.source)
        self.vehicleDestination = self.vehicleSetting.destination

        self.statDataframe = pd.DataFrame()
        self.initStats()

    
    def reset(self, seed=1):
        """Only used for episodic simulator
        """
        self.logger.info(f"Resetting environment")
        # self.pedFactory.reset()
        # self.vehicleFactory.reset()
        self.destoryActors()

        self.walkerActors: List[WalkerActor] = []

        super().reset(seed)

        self.episodeNumber += 1
        self.episodeTimeStep = 0
        self.createDynamicAgents()
        self.setupSimulator(episodic=True)
                
        self.initStats()

        self.logger.warn(f"started episode {self.episodeNumber}")

        
    
    #region actor generation

    def getVehicleSetting(self) -> SourceDestinationPair:
        vehicleSetting = self.settingsManager.getVehicleSettings()
        vehicleSetting = vehicleSetting[0]
        return vehicleSetting
    
    @abstractmethod
    def createWalkers(self):
        raise NotImplementedError("createWalkers not implemented")
        pass


    @abstractmethod
    def resetWalkers(self):
        raise NotImplementedError("resetWalkers not implemented")
        pass


    # def getWalkerCrossingAxisRotation(self):
        
    #     wp = self.map.get_waypoint(self.walkerSetting.source)
    #     wpTransform = wp.transform
    #     # walkerXAxisDirection = wpTransform.get_forward_vector()
    #     return wpTransform.rotation.yaw

    
    def createVehicle(self, randomizeSpawnPoint=False):
        maxSpeed = random.choice([10, 14, 18, 22])
        self.vehicle, self.vehicleAgent = super().createVehicle(self.getVehicleSetting(), maxSpeed=maxSpeed, randomizeSpawnPoint=randomizeSpawnPoint)


    def resetVehicle(self):
        # destroy current one
        # self.simulator.removeOnTicker()
        self.logger.warn(f"Recreating vehicle")
        self.vehicleFactory.destroy(self.vehicle)
        self.vehicleAgent = None
        self.vehicle = None
        self.createVehicle()

    def resetWalker(self, sameOrigin=True):
        self.logger.warn(f"Resetting Walker")
        raise NotImplementedError("Use resetWalkers instead")


    
    def createDynamicAgents(self):
        
        self.createVehicle()
        
        self.tickOrWaitBeforeSimulation() # otherwise we can get wrong vehicle location!
        self.createWalkers()
        pass

    def recreateDynamicAgents(self):
        raise NotImplementedError("recreateDynamicAgents not implemented")
        # 1. recreated vehicle
        self.recreateVehicle()
        self.tickOrWaitBeforeSimulation() # otherwise we can get wrong vehicle location!

        # 2. reset walker
        self.resetWalker(sameOrigin=True)
        self.walkerAgent.setEgoVehicle(self.vehicle)

        pass
    
    
    #endregion

    #region simulation

    def setupSimulator(self, episodic=False):
        """Must be called after all actors are created.

        Args:
            episodic (bool, optional): _description_. Defaults to False.
        """
        # self.episodeNumber = 1 # updated when resetted

        onTickers = [self.visualizer.onTick, self.onTick] # onTick must be called before restart
        # terminalSignalers = [self.walkerAgent.isFinished]
        terminalSignalers = [walkerActor.agent.isFinished for walkerActor in self.walkerActors] # TODO, improve it so that all has to finish.

        if episodic:
            # this is only to be used from gym environments. It does not call onEnd as we may reset and run
            self.simulator = EpisodeSimulator(
                self.client, 
                terminalSignalers=terminalSignalers, 
                onTickers=onTickers, 
                onEnders=[], 
                simulationMode=self.simulationMode
            )
        else:
            onEnders = [self.onEnd]
            onTickers.append(self.restart)
            self.simulator = Simulator(
                self.client, 
                onTickers=onTickers, 
                onEnders=onEnders, 
                simulationMode=self.simulationMode
            )



    def run(self, maxTicks=1000):
        """Runs in asynchronous mode only

        Args:
            maxTicks (int, optional): _description_. Defaults to 1000.
        """

        # self.episodeNumber = 1 # updated when resetted
        

        # self.visualizer.drawPoint(carla.Location(x=-96.144363, y=-3.690280, z=1), color=(0, 0, 255), size=0.1)
        # self.visualizer.drawPoint(carla.Location(x=-134.862671, y=-42.092407, z=0.999020), color=(0, 0, 255), size=0.1)

        # return

        try:

            self.createDynamicAgents()
            
            # self.world.wait_for_tick()
            self.tickOrWaitBeforeSimulation()

            self.setupSimulator(False)

            self.simulator.run(maxTicks)
        except Exception as e:
            self.logger.exception(e)
            self.destoryActors()

        # try: 
        # except Exception as e:
        #     self.logger.exception(e)
    #endregion


    def restart(self):
        """Used by non-episodic simulator only
        """

        killCurrentEpisode = False
        
        if self.walkerAgent.isFinished():
            self.episodeNumber += 1
            self.episodeTimeStep = 0
            killCurrentEpisode = True

        if self.episodeTimeStep > 200:
            self.episodeTimeStep = 0
            killCurrentEpisode = True
            self.logger.info("Killing current episode as it takes more than 200 ticks")
        
        if killCurrentEpisode:

            self.recreateDynamicAgents()
            # 3. update statDataframe
            self.initStats()

    
    
    def onEnd(self):
        self.logger.warn(f"ending simulation")
        self.destoryActors()
        self.saveStats()

    def onTick(self, world_snapshot):

        self.episodeTimeStep += 1

        self.collectStats()


        for walkerActor in self.walkerActors:
            walkerActor.agent.onTickStart(world_snapshot)
            self.updateWalker(world_snapshot, walkerActor.agent, walkerActor.carlaActor)

        self.updateVehicle(world_snapshot, self.vehicleAgent, self.vehicle)

        # draw waypoints upto walker
        # self.drawWaypointsToWalker()

    def drawWaypointsToWalker(self):
        walkerWp = self.map.get_waypoint(self.walkerAgent.location).transform.location
        waypoints = Utils.getWaypointsToDestination(self.vehicle, walkerWp)
        self.visualizer.drawWaypoints(waypoints, color=(0, 0, 0), z=1, life_time=0.1)
        self.logger.info(f"Linear distance to pedestrian {self.walkerAgent.actorManager.distanceFromNearestOncomingVehicle()}")
        self.logger.info(f"Arc distance to pedestrian {Utils.getDistanceCoveredByWaypoints(waypoints)}")
    
    
    #region stats
  
    def addActorsToRecorder(self, recorder: EpisodeTrajectoryRecorder):
        recorder.addPedestrian(self.walkerAgent, self.episodeTimeStep, self.getWalkerSetting().toDict())
        recorder.addVehicle(self.vehicleAgent, self.episodeTimeStep, self.getVehicleSetting().toDict())

    
    #endregion