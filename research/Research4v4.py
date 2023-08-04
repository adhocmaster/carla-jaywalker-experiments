from genericpath import sameopenfile
from turtle import distance
from typing import List, Tuple
import carla
import logging
import random
import os
import numpy as np
import json
from datetime import date

from agents.pedestrians.soft import Direction, LaneSection, NavPath, NavPoint
from research.SettingBasedResearch import SettingBasedResearch
from settings.SourceDestinationPair import SourceDestinationPair

from .BaseResearch import BaseResearch
from settings.circular_t_junction_settings import circular_t_junction_settings
from settings.town02_settings import town02_settings
from settings.town03_settings import town03_settings
from settings.varied_width_lanes_settings import varied_width_lanes_settings
from settings import SettingsManager
from agents.pedestrians import PedestrianFactory
from agents.pedestrians.PedestrianAgent import PedestrianAgent
from agents.pedestrians.factors import Factors
from agents.vehicles import VehicleFactory

from agents.navigation.behavior_agent import BehaviorAgent
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
        
        self.walkers: List[carla.Walker] = []
        self.walkerAgents: List[PedestrianAgent] = []
        self.vehicles: List[carla.Vehicle] = []
        self.vehicleAgents: List[BehaviorAgent] = []

        self._navPath = None

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

        for vehicleSetting, walkerSetting in self.getVehicleWalkerSettingsPairs():
            vehicle, vehicleAgent = self.createVehicle(vehicleSetting)
            self.vehicles.append(vehicle)
            self.vehicleAgents.append(vehicleAgent)

            self.tickOrWaitBeforeSimulation() # otherwise we can get wrong vehicle location!
            walker, walkerAgent = self.createWalker(vehicle, walkerSetting)
            self.walkers.append(walker)
            self.walkerAgents.append(walkerAgent)
        
        pass

    def recreateDynamicAgents(self):
       
        self.vehicleAgents.clear()
        self.logger.info('\ndestroying  vehicles')
        self.vehicleFactory.reset()

        for idx, (vehicleSetting, walkerSetting) in enumerate(self.getVehicleWalkerSettingsPairs()):
            vehicle, vehicleAgent = self.createVehicle(vehicleSetting)
            self.vehicles.append(vehicle)
            self.vehicleAgents.append(vehicleAgent)

            self.tickOrWaitBeforeSimulation() # otherwise we can get wrong vehicle location!
            self.resetWalker(vehicle, self.walkerAgents[idx], walkerSetting)

        pass
    

    
    def getVehicleWalkerSettingsPairs(self) -> List[Tuple[SourceDestinationPair, SourceDestinationPair]]:
        
        walkerSettings = self.settingsManager.getWalkerSettings()
        vehicleSettings = self.settingsManager.getVehicleSettings()

        pairs = []
        for idx in range(len(vehicleSettings)):
            if idx < len(walkerSettings):
                pairs.append((vehicleSettings[idx], walkerSettings[idx]))

        return pairs
    
    def createVehicle(self, vehicleSetting: SourceDestinationPair) -> Tuple[carla.Vehicle, BehaviorAgent]:
        vehicleSpawnPoint = self.settingsManager.locationToVehicleSpawnPoint(vehicleSetting.source)
        
        vehicle = self.vehicleFactory.spawn(vehicleSpawnPoint)       
        if vehicle is None:
            self.logger.error("Cannot spawn vehicle")
            exit("Cannot spawn vehicle")
        else:
            self.logger.info(f"successfully spawn vehicle at {vehicleSpawnPoint.location.x, vehicleSpawnPoint.location.y, vehicleSpawnPoint.location.z}")

        self.tickOrWaitBeforeSimulation() # otherwise we can get wrong vehicle location!

        # self.vehicleAgent = self.vehicleFactory.createAgent(self.vehicle, target_speed=20, logLevel=logging.DEBUG)
        # self.vehicleAgent = self.vehicleFactory.createBehaviorAgent(self.vehicle, behavior='cautious', logLevel=logging.DEBUG)
        max_speed = random.choice([10, 14, 18, 22])
        vehicleAgent = self.vehicleFactory.createSpeedControlledBehaviorAgent(vehicle, max_speed=max_speed, behavior='normal', logLevel=logging.INFO)

        spawnXYLocation = carla.Location(x=vehicleSpawnPoint.location.x, y=vehicleSpawnPoint.location.y, z=0.001)

        destination = vehicleSetting.destination


        vehicleAgent.set_destination(destination, start_location=spawnXYLocation)
        # raise Exception("stop")
        plan = vehicleAgent.get_local_planner().get_plan()
        # Utils.draw_trace_route(self._vehicle.get_world().debug, plan)
        self.visualizer.drawTraceRoute(plan, color=(10, 10, 0, 0), life_time=15.0)
        self.visualizer.drawDestinationPoint(destination, color=(0, 0, 255, 0), life_time=15.0)

        return vehicle, vehicleAgent

    def createWalker(self, vehicle: carla.Vehicle, walkerSetting: SourceDestinationPair) -> Tuple[carla.Walker, PedestrianAgent]:

        walkerSpawnPoint = carla.Transform(location = walkerSetting.source)
        
        self.visualizer.drawWalkerNavigationPoints([walkerSpawnPoint])


        walker = self.pedFactory.spawn(walkerSpawnPoint)

        if walker is None:
            self.logger.error("Cannot spawn walker")
            exit("Cannot spawn walker")
        else:
            self.logger.info(f"successfully spawn walker {walker.id} at {walkerSpawnPoint.location.x, walkerSpawnPoint.location.y, walkerSpawnPoint.location.z}")
            self.logger.info(walker.get_control())
            
            # visualizer.trackOnTick(walker.id, {"life_time": 1})      
        
        # self.world.wait_for_tick() # otherwise we can get wrong agent location!
        self.tickOrWaitBeforeSimulation()


        walkerAgent = self.pedFactory.createAgent(walker=walker, logLevel=self.logLevel, optionalFactors=[], config=None)

        walkerDestination = walkerSetting.destination

        walkerAgent.setDestination(walkerDestination)
        self.visualizer.drawDestinationPoint(walkerDestination, life_time=15.0)
        walkerAgent.setEgoVehicle(vehicle)


        # self.setWalkerNavPath()
        self.setWalkerDebugSettings(walkerAgent, walkerSetting)
        # self.walkerAgent.debug = False

        # self.walkerAgent.updateLogLevel(logging.INFO)

        
        walkerAgent.setNavPath(self.navPath)

        return walker, walkerAgent


        pass


    def resetWalker(self, vehicle: carla.Vehicle, walkerAgent:PedestrianAgent, walkerSetting: SourceDestinationPair, sameOrigin=True):

        self.logger.warn(f"Resetting Walker")
        walkerAgent.setEgoVehicle(vehicle)
        

        if sameOrigin == True:
            
            walkerAgent.reset(newStartPoint=walkerSetting.source)
            walkerAgent.setDestination(walkerSetting.destination)

        elif walkerAgent.location.distance_2d(walkerSetting.source) < 1: # currently close to source
            walkerAgent.reset()
            walkerAgent.setDestination(walkerSetting.destination)
        else:
            walkerAgent.reset()
            walkerAgent.setDestination(walkerSetting.source)
        



    def setWalkerDebugSettings(self, walkerAgent: PedestrianAgent, walkerSetting: SourceDestinationPair):
        walkerSpawnPoint = carla.Transform(location = walkerSetting.source)

        walkerAgent.debug = False
        walkerAgent.updateLogLevel(logging.WARN)

        visualizationForceLocation = self.settingsManager.getVisualizationForceLocation()
        if visualizationForceLocation is None:
            visualizationForceLocation = walkerSpawnPoint.location
        
        visualizationInfoLocation = carla.Location(x=visualizationForceLocation.x + 2, y=visualizationForceLocation.y + 2, z=visualizationForceLocation.z)

        
        walkerAgent.visualizationForceLocation = visualizationForceLocation
        walkerAgent.visualizationInfoLocation = visualizationInfoLocation

    
    #region simulation

    def setupSimulator(self, episodic=False):
        """Must be called after all actors are created.

        Args:
            episodic (bool, optional): _description_. Defaults to False.
        """
        # self.episodeNumber = 1 # updated when resetted

        onTickers = [self.visualizer.onTick, self.onTick] # onTick must be called before restart
        terminalSignalers = [walkerAgent.isFinished for walkerAgent in self.walkerAgents]

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

        # endregion

    
    def destoryActors(self):
        
        self.logger.info('\ndestroying  walkers')
        self.pedFactory.reset()
        self.logger.info('\ndestroying  vehicles')
        self.vehicleFactory.reset()

    def restart(self, world_snapshot):

        areWalkersFinished = True
        for walkerAgent in self.walkerAgents:
            if not walkerAgent.isFinished():
                areWalkersFinished = False
                break
        

        killCurrentEpisode = False
        
        if areWalkersFinished:
            self.episodeNumber += 1
            self.episodeTimeStep = 0
            killCurrentEpisode = True

        if self.episodeTimeStep > 50:
            self.episodeTimeStep = 0
            killCurrentEpisode = True
            self.logger.info("Killing current episode as it takes more than 200 ticks")
        
        if killCurrentEpisode:

            self.logger.warn(f"Killing current episode. Episode number: {self.episodeNumber}")

            self.recreateDynamicAgents()
            # 3. update statDataframe
            # self.updateStatDataframe()

    
    def onEnd(self):
        self.logger.warn(f"ending simulation")
        self.destoryActors()
        # self.saveStats()

    def onTick(self, world_snapshot):

        self.episodeTimeStep += 1

        # self.collectStats(world_snapshot)

        for idx, walkerAgent in enumerate(self.walkerAgents):
            walkerAgent.onTickStart(world_snapshot)
            self.updateWalker(world_snapshot, walkerAgent, self.walkers[idx])

        for idx, vehicleAgent in enumerate(self.vehicleAgents):
            self.updateVehicle(world_snapshot, vehicleAgent, self.vehicles[idx])


            
    def updateWalker(self, world_snapshot, walkerAgent: PedestrianAgent, walker: carla.Walker):

        # print("updateWalker")
        if not walker.is_alive:
            return
        
        if walkerAgent is None:
            self.logger.warn(f"No walker to update")
            return

        if walkerAgent.isFinished():
            self.logger.warn(f"Walker {walkerAgent.walker.id} reached destination")
            walker.apply_control(walkerAgent.getStopControl())
            return
        
        control = walkerAgent.calculateControl()
        # print("apply_control")
        walker.apply_control(control)
            
    def updateVehicle(self, world_snapshot, vehicleAgent: BehaviorAgent, vehicle: carla.Vehicle):
        if not vehicle.is_alive:
            return

        if vehicleAgent is None:
            self.logger.warn(f"No vehicle to update")
            return 

        if vehicleAgent.done():
            self.logger.info(f"vehicle {vehicle.id} reached destination")
            vehicle.apply_control(carla.VehicleControl())
            return

        
        control = vehicleAgent.run_step()
        control.manual_gear_shift = False
        self.logger.info(control)
        vehicle.apply_control(control)
        pass

