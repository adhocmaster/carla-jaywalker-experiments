from abc import abstractmethod
from datetime import date
import json
import math
import logging
import random
import numpy as np
from typing import Tuple

import pandas as pd
from agents.navigation.behavior_agent import BehaviorAgent
from agents.pedestrians.PedestrianAgent import PedestrianAgent
import carla
import os
from analysis.EpisodeTrajectoryRecorder import EpisodeTrajectoryRecorder
from lib import ClientUser, LoggerFactory, MapManager, MapNames, SimulationVisualization, NotImplementedInterface, SimulationMode
from lib.ActorClass import ActorClass
from settings.SourceDestinationPair import SourceDestinationPair
# from lib.SimulationMode import SimulationMode

class BaseResearch(ClientUser):
    def __init__(
            self, 
            name, 
            client: carla.Client, 
            mapName, logLevel, 
            outputDir:str = "logs", 
            simulationMode = SimulationMode.ASYNCHRONOUS,
            record=False, 
            render=True,
            stats=False,
            ignoreStatsSteps=0,
        ) -> None:
        super().__init__(client)

        self.name = name
        self.mapName = mapName
        self.logLevel = logLevel
        self.outputDir = outputDir

        logPath = os.path.join(outputDir, f"{name}.log")
        self.logger = LoggerFactory.getBaseLogger(name, defaultLevel=logLevel, file=logPath)

        self.simulationMode = simulationMode
        self.record = record
        self.render = render
        self.stats = stats
        self.ignoreStatsSteps = ignoreStatsSteps
        self.episodeTrajectoryRecorders = {}
        
        self.episodeNumber = 0
        self.episodeTimeStep = 0

        self.time_delta = None
        self.mapManager = None
        self.visualizer = None
        self.mapManager: MapManager = None


        self.initWorldSettings()
        self.initVisualizer()

        pass


    def configureMap(self):
        self.mapManager = MapManager(self.client)
        self.mapManager.load(self.mapName, forceReload=True)

    def reset(self, seed=1):
        # self.client.reload_world(False)
        self.mapManager.reload()
        print(f"resetting world with seed {seed}")
        random.seed(seed)
        np.random.seed(seed)


    def initWorldSettings(self):
        # settings = self.world.get_settings()
        # settings.substepping = False
        # settings.fixed_delta_seconds = self.time_delta
        # self.world.apply_settings(settings)
        
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.logger.warn(f"Starting simulation in asynchronous mode")
            self.initWorldSettingsAsynchronousMode()
        else:
            self.logger.warn(f"Starting simulation in synchronous mode")
            self.initWorldSettingsSynchronousMode()

        
        settings = self.world.get_settings()
        if not self.render:
            settings.no_rendering_mode = True
        
        self.world.apply_settings(settings)

        pass

    
    def initVisualizer(self):
        self.visualizer = SimulationVisualization(self.client, self.mapManager)
        self.visualizer.drawSpawnPoints(life_time=1.0)
        self.visualizer.drawSpectatorPoint()
        # self.visualizer.drawAllWaypoints(life_time=1.0)
        pass

    def initWorldSettingsAsynchronousMode(self):
        self.configureMap()
        self.time_delta = 0.007
        settings = self.world.get_settings()
        settings.synchronous_mode = False # Enables asynchronous mode
        # settings.substepping = False # set it to true for faster execution. It has no effect on asynchronous mode
        settings.substepping = True # https://carla.readthedocs.io/en/latest/adv_synchrony_timestep/#physics-substepping
        settings.max_substeps = 10
        settings.max_substep_delta_time = self.time_delta / settings.max_substeps
        settings.fixed_delta_seconds = self.time_delta
        print("applying settings", settings)
        self.world.apply_settings(settings)
        pass

    def initWorldSettingsSynchronousMode(self):
        self.configureMap()
        self.time_delta = 0.04
        settings = self.world.get_settings()
        settings.synchronous_mode = True # Enables synchronous mode
        settings.fixed_delta_seconds = self.time_delta # Sets fixed time step
        
        # settings.substepping = False # set it to true for faster execution. It has no effect on synchronous mode
        settings.substepping = True # https://carla.readthedocs.io/en/latest/adv_synchrony_timestep/#physics-substepping
        settings.max_substeps = 2
        settings.max_substep_delta_time = self.time_delta / settings.max_substeps
        # print("applying settings", settings)
        self.world.apply_settings(settings)
        pass

    def tickOrWaitBeforeSimulation(self):
        """
        It will not call simulation events. Only purpose is for some intializations which needs to be applied before simulation runs, e.g., actor creation.
        """
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.world.wait_for_tick()
        else:
            self.world.tick()

    @abstractmethod
    def createDynamicAgents(self):
        raise NotImplementedInterface("createDynamicAgents")

    @abstractmethod
    def setupSimulator(self):
        raise NotImplementedInterface("setupSimulator")
    

    # region actor utility methods
    
    def createVehicle(
            self, 
            vehicleSetting: SourceDestinationPair, 
            maxSpeed: float, 
            logLevel=logging.INFO, 
            randomizeSpawnPoint=False
        ) -> Tuple[carla.Vehicle, BehaviorAgent]:
        
        vehicleSpawnPoint = self.settingsManager.locationToVehicleSpawnPoint(vehicleSetting.source)
        
        if randomizeSpawnPoint:
            currentWp = self.map.get_waypoint(vehicleSpawnPoint.location)
            distance = random.random() * 10 # 0 to 10 meter gap
            # vehicleSpawnPoint = currentWp.next(distance)[0].transform
            if np.random.choice([True, False]): # back for forward
                vehicleSpawnPoint = currentWp.next(distance)[0].transform
            else:
                vehicleSpawnPoint = currentWp.previous(distance)[0].transform
            vehicleSpawnPoint.location += carla.Location(z=1)

        vehicle = self.vehicleFactory.spawn(vehicleSpawnPoint)       
        if vehicle is None:
            self.logger.error("Cannot spawn vehicle")
            exit("Cannot spawn vehicle")
        else:
            self.logger.info(f"successfully spawn vehicle at {vehicleSpawnPoint.location.x, vehicleSpawnPoint.location.y, vehicleSpawnPoint.location.z}")

        self.tickOrWaitBeforeSimulation() # otherwise we can get wrong vehicle location!

        vehicleAgent = self.vehicleFactory.createSpeedControlledBehaviorAgent(vehicle, max_speed=maxSpeed, behavior='normal', logLevel=logLevel)

        spawnXYLocation = carla.Location(x=vehicleSpawnPoint.location.x, y=vehicleSpawnPoint.location.y, z=0.001)

        destination = vehicleSetting.destination
        vehicleAgent.set_destination(destination, start_location=spawnXYLocation)

        # raise Exception("stop")
        plan = vehicleAgent.get_local_planner().get_plan()
        # Utils.draw_trace_route(self._vehicle.get_world().debug, plan)
        self.visualizer.drawTraceRoute(plan, color=(10, 10, 0, 0), life_time=15.0)
        self.visualizer.drawDestinationPoint(destination, color=(0, 0, 255, 0), life_time=15.0)

        return vehicle, vehicleAgent
    
    def createWalker(self, walkerSetting: SourceDestinationPair) -> Tuple[carla.Walker, PedestrianAgent]:

        walkerSpawnPoint = carla.Transform(location = walkerSetting.source)
        
        self.visualizer.drawWalkerNavigationPoints([walkerSpawnPoint])


        print("walkerSpawnPoint", walkerSpawnPoint)
        walker = self.pedFactory.spawn(walkerSpawnPoint)

        if walker is None:
            self.logger.error(f"Cannot spawn walker at {walkerSetting.source}")
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

        self.setWalkerDebugSettings(walkerAgent, walkerSetting)

        return walker, walkerAgent


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
        
        # print(f"vehicle speed {vehicle.get_velocity().length() * 3.6} km/h")

        
        control = vehicleAgent.run_step()
        control.manual_gear_shift = False
        self.logger.debug(control)
        vehicle.apply_control(control)
        pass

    
    
    def destoryActors(self):
        
        self.logger.info('\ndestroying  walkers')
        self.pedFactory.reset()
        self.logger.info('\ndestroying  vehicles')
        self.vehicleFactory.reset()

    
    # endregion

    # region stats


    def initStats(self):

        if not self.stats:
            return

        pass
    
    
    def collectStats(self):
        if not self.stats or self.episodeTimeStep < self.ignoreStatsSteps:
            return

        self.initEpisodeRecorderIfNeeded()
        self.recordTrajectoryTimeStep()

        pass

    def initEpisodeRecorderIfNeeded(self):
        if self.episodeNumber not in self.episodeTrajectoryRecorders:
            self.episodeTrajectoryRecorders[self.episodeNumber] = EpisodeTrajectoryRecorder(
                self.episodeNumber,
                self.world.get_snapshot(),
                {}, # TODO road configuration
                fps = 1 / self.time_delta,
                startFrame=self.episodeTimeStep
            )


    def recordTrajectoryTimeStep(self):
        # self.logger.warn("recordTrajectoryTimeStep")
        recorder = self.episodeTrajectoryRecorders[self.episodeNumber]
        self.addActorsToRecorder(recorder)
        recorder.collectStats(self.episodeTimeStep)

    @abstractmethod
    def addActorsToRecorder(self, recorder: EpisodeTrajectoryRecorder):
        # recorder.addActor(self.walker, ActorClass.pedestrian, self.episodeTimeStep, self.getWalkerSetting().toDict())
        # recorder.addPedestrian(self.walkerAgent, self.episodeTimeStep, self.getWalkerSetting().toDict())
        # recorder.addActor(self.vehicle, ActorClass.vehicle, self.episodeTimeStep, self.getVehicleSetting().toDict())
        raise NotImplementedInterface("addActorsToRecorder")


    def saveStats(self):
        if not self.stats:
            return

        self.saveTrajectories()

        pass


    def saveTrajectories(self):

        dfs = []
        meta = []
        for recorder in self.episodeTrajectoryRecorders.values():
            episodeDf = recorder.getAsDataFrame()
            dfs.append(episodeDf)

            meta.append(recorder.getMeta())

        simDf = pd.concat(dfs, ignore_index=True)

        dateStr = date.today().strftime("%Y-%m-%d")
        statsPath = os.path.join(self.outputDir, f"{self.name}-{dateStr}-tracks.csv")
        self.logger.warn(f"Saving tracks to {statsPath}")
        simDf.to_csv(statsPath, index=False)

        metaPath = os.path.join(self.outputDir, f"{self.name}-{dateStr}-meta.json")
        
        with open(metaPath, "w") as outfile:
            # print(meta)
            outfile.write(json.dumps(meta, indent=2))


    
    #endregion