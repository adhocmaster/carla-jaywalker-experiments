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
from settings.SourceDestinationPair import SourceDestinationPair

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

class Research1v1(SettingBasedResearch):
    
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

        self.name = "Research1v1"

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

        self.setup()

    #region getters
    def getVehicle(self):
        return self.vehicle

    def getWalker(self):
        return self.walker

    def getVehicleAgent(self):
        return self.vehicleAgent

    def getWalkerAgent(self):
        return self.walkerAgent

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

        self.walker = None
        self.walkerAgent = None
        self._walkerSetting = None
        # self.walkerSetting = self.getWalkerSetting()

    

        self.vehicle = None
        self.vehicleAgent = None
        self.vehicleSetting = self.getVehicleSetting()
        self.vehicleSpawnPoint = self.settingsManager.locationToVehicleSpawnPoint(self.vehicleSetting.source)
        self.vehicleDestination = self.vehicleSetting.destination

        self.statDataframe = pd.DataFrame()
        self.initStatDict()

    
    def reset(self):
        """Only used for episodic simulator
        """
        self.logger.info(f"Resetting environment")
        # self.pedFactory.reset()
        # self.vehicleFactory.reset()
        self.destoryActors()

        super().reset()

        self.episodeNumber += 1
        self.episodeTimeStep = 0
        self.createDynamicAgents()
        self.setupSimulator(episodic=True)

        self.logger.warn(f"started episode {self.episodeNumber}")

        
    
    #region actor generation

    @property
    def walkerSetting(self):
        return self._walkerSetting

    def getWalkerSetting(self, reverse=False):
        if self._walkerSetting is None:
            walkerSettings = self.settingsManager.getWalkerSettings()
            walkerSetting = walkerSettings[0]
            if reverse:
                walkerSetting = self.settingsManager.reverseWalkerSetting(walkerSetting)
            
            self._walkerSetting = walkerSetting

        return self._walkerSetting

    def getVehicleSetting(self):
        vehicleSetting = self.settingsManager.getVehicleSettings()
        vehicleSetting = vehicleSetting[0]
        return vehicleSetting

    def createWalker(self, reverse=False):
        
        self.walker, self.walkerAgent = super().createWalker(self.getWalkerSetting(reverse=reverse))

        pass


    def getWalkerCrossingAxisRotation(self):
        
        wp = self.map.get_waypoint(self.walkerSetting.source)
        wpTransform = wp.transform
        # walkerXAxisDirection = wpTransform.get_forward_vector()
        return wpTransform.rotation.yaw

    
    def createVehicle(self, randomizeSpawnPoint=False):
        maxSpeed = random.choice([10, 14, 18, 22])
        self.vehicle, self.vehicleAgent = super().createVehicle(self.getVehicleSetting(), maxSpeed=maxSpeed, randomizeSpawnPoint=randomizeSpawnPoint)


    def recreateVehicle(self):
        # destroy current one
        # self.simulator.removeOnTicker()
        self.logger.warn(f"Recreating vehicle")
        self.vehicleFactory.destroy(self.vehicle)
        self.vehicleAgent = None
        self.vehicle = None
        self.createVehicle()

    def resetWalker(self, sameOrigin=True):
        self.logger.warn(f"Resetting Walker")
        self.walkerAgent.setEgoVehicle(self.vehicle)

        if sameOrigin == True:
            
            self.walkerAgent.reset(newStartPoint=self.walkerSetting.source)
            self.walkerAgent.setDestination(self.walkerSetting.destination)

        elif self.walkerAgent.location.distance_2d(self.walkerSetting.source) < 1: # currently close to source
            self.walkerAgent.reset()
            self.walkerAgent.setDestination(self.walkerSetting.destination)
        else:
            self.walkerAgent.reset()
            self.walkerAgent.setDestination(self.walkerSetting.source)


    
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
    
    
    #endregion

    #region simulation

    def setupSimulator(self, episodic=False):
        """Must be called after all actors are created.

        Args:
            episodic (bool, optional): _description_. Defaults to False.
        """
        # self.episodeNumber = 1 # updated when resetted

        onTickers = [self.visualizer.onTick, self.onTick] # onTick must be called before restart
        terminalSignalers = [self.walkerAgent.isFinished]

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


    def restart(self, world_snapshot):

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
            self.updateStatDataframe()

    
    
    def onEnd(self):
        self.logger.warn(f"ending simulation")
        self.destoryActors()
        self.saveStats()

    def onTick(self, world_snapshot):

        self.episodeTimeStep += 1

        self.collectStats(world_snapshot)

        self.walkerAgent.onTickStart(world_snapshot)

        self.updateWalker(world_snapshot, self.walkerAgent, self.walker)
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

    def updateStatDataframe(self):
        if not self.stats:
            return
        # 1. make a dataframe from self.statDict
        df = pd.DataFrame.from_dict(self.statDict)
        # 2. merge it with the statDataframe
        self.statDataframe = pd.concat([self.statDataframe, df], ignore_index=True)
        # 3. clear self.statDict
        self.initStatDict()


    def initStatDict(self):

        if not self.stats:
            return

        self.statDict = {
            "episode": [], 
            "timestep": [],
            "v_x": [], 
            "v_y": [], 
            "v_speed": [], 
            # "v_direction": [], 
            "w_x": [], 
            "w_y": [], 
            "w_speed": [], 
            "w_state": []
            # "w_direction": []
        }

        self.episodeTrajectoryRecorders = {}


        pass
    
    def collectStats(self, world_snapshot):
        if not self.stats:
            return

        self.statDict["episode"].append(self.episodeNumber)
        self.statDict["timestep"].append(self.episodeTimeStep)
        self.statDict["v_x"].append(self.vehicle.get_location().x)
        self.statDict["v_y"].append(self.vehicle.get_location().y)
        self.statDict["v_speed"].append(self.vehicle.get_velocity().length())
        # self.statDict["v_direction"].append(self.episodeNumber)
        self.statDict["w_x"].append(self.walkerAgent.location.x)
        self.statDict["w_y"].append(self.walkerAgent.location.y)

        if self.walkerAgent.isMovingTowardsDestination():
            self.statDict["w_speed"].append(self.walkerAgent.speed)
        else:
            self.statDict["w_speed"].append(-self.walkerAgent.speed)
        # self.statDict["w_direction"].append(self.episodeNumber)
        self.statDict["w_state"].append(self.walkerAgent.state.value)


        self.initEpisodeRecorderIfNeeded()
        self.recordTrajectoryTimeStep()

        pass

    def initEpisodeRecorderIfNeeded(self):
        if self.episodeNumber not in self.episodeTrajectoryRecorders:
            self.episodeTrajectoryRecorders[self.episodeNumber] = EpisodeTrajectoryRecorder(
                self.episodeNumber,
                {}, # TODO road configuration
                fps = 1 / self.time_delta,
                startFrame=self.episodeTimeStep
            )


    def recordTrajectoryTimeStep(self):
        # self.logger.warn("recordTrajectoryTimeStep")
        recorder = self.episodeTrajectoryRecorders[self.episodeNumber]
        self.addActorsToRecorder(recorder)
        recorder.collectStats(self.episodeTimeStep)

    def addActorsToRecorder(self, recorder: EpisodeTrajectoryRecorder):
        recorder.addactor(self.walker, ActorClass.pedestrian, self.episodeTimeStep)
        recorder.addactor(self.vehicle, ActorClass.vehicle, self.episodeTimeStep)


    def saveStats(self):
        if not self.stats:
            return

        self.saveTrajectories()


        dateStr = date.today().strftime("%Y-%m-%d-%H-%M")
        statsPath = os.path.join(self.outputDir, f"{dateStr}-trajectories.csv")
        # df = pd.DataFrame.from_dict(self.statDict)
        # df.to_csv(statsPath, index=False)

        if len(self.statDataframe) == 0:
            self.logger.warn("Empty stats. It means no episode was completed in this run")
            return
        self.statDataframe.to_csv(statsPath, index=False)
        pass


    def saveTrajectories(self):

        dfs = []
        meta = [{
            "crossingAxisRotation" : self.getWalkerCrossingAxisRotation(),
            "walkerSource": (self.walkerSetting.source.x, self.walkerSetting.source.y),
            "walkerDestination" : (self.walkerSetting.destination.x, self.walkerSetting.destination.y)
        }]
        for recorder in self.episodeTrajectoryRecorders.values():
            episodeDf = recorder.getAsDataFrame()
            dfs.append(episodeDf)

            meta.append(recorder.getMeta())

        simDf = pd.concat(dfs, ignore_index=True)

        dateStr = date.today().strftime("%Y-%m-%d-%H-%M")
        statsPath = os.path.join(self.outputDir, f"{dateStr}-tracks.csv")
        self.logger.warn(f"Saving tracks to {statsPath}")
        simDf.to_csv(statsPath, index=False)

        metaPath = os.path.join(self.outputDir, f"{dateStr}-meta.json")
        
        with open(metaPath, "w") as outfile:
            outfile.write(json.dumps(meta))


        # meta


    
    #endregion