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

class Research1v1(BaseResearch):
    
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

        # self.optionalFactors = [Factors.DRUNKEN_WALKER]
        self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE]
        # self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE, Factors.SURVIVAL_DESTINATION]
        # self.optionalFactors = [Factors.ANTISURVIVAL]
        # self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE, Factors.SURVIVAL_DESTINATION]
        # self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE, Factors.SURVIVAL_DESTINATION, Factors.DRUNKEN_WALKER]
        # self.optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE, Factors.DRUNKEN_WALKER]
        # self.optionalFactors = []

        # self.optionalFactors = [Factors.SURVIVAL_DESTINATION, Factors.DRUNKEN_WALKER, Factors.FREEZING_FACTOR]

#        self.optionalFactors = [Factors.SURVIVAL_DESTINATION, Factors.FREEZING_FACTOR]


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
        if self.walker is not None:
            # self.walker.destroy()
            self.pedFactory.destroy(self.walker)

        self.logger.info('\ndestroying  vehicles')
        if self.vehicle is not None:
            self.vehicleFactory.destroy(self.vehicle)

    
    def setMap(self, mapName:MapNames):
        raise Exception('map cannot be changed for a research setting')

    def setSettings(self, settingsId):
        self.settingsId = settingsId
        self.setup()


    def setup(self):
        # self.settingsManager.load("setting3")
        # return 
        self.settingsManager.load(self.settingsId)

        self.walker = None
        self.walkerAgent = None
        self.walkerSetting = self.getWalkerSetting()
        self.walkerSpawnPoint = carla.Transform(location = self.walkerSetting.source)
        self.walkerDestination = self.walkerSetting.destination

        self.vehicle = None
        self.vehicleAgent = None
        self.vehicleSetting = self.getVehicleSetting()
        self.vehicleSpawnPoint = self.settingsManager.locationToVehicleSpawnPoint(self.vehicleSetting.source)
        self.vehicleDestination = self.vehicleSetting.destination

        self.simulator = None # populated when run

        self.statDataframe = pd.DataFrame()
        self.initStatDict()

    
    def reset(self):
        """Does not reset episode number. Only used for episodic simulator
        """
        self.logger.info(f"Resetting environment")
        self.pedFactory.reset()
        self.vehicleFactory.reset()

        super().reset()

        self.episodeTimeStep = 0
        self.createDynamicAgents()
        self.setupSimulator(episodic=True)

        
    
    #region actor generation

    def getWalkerSetting(self):
        walkerSettings = self.settingsManager.getWalkerSettings()
        walkerSetting = walkerSettings[0]
        return walkerSetting

    def getVehicleSetting(self):
        vehicleSetting = self.settingsManager.getVehicleSettings()
        vehicleSetting = vehicleSetting[0]
        return vehicleSetting

    def createWalker(self):
        
        self.visualizer.drawWalkerNavigationPoints([self.walkerSpawnPoint])


        self.walker = self.pedFactory.spawn(self.walkerSpawnPoint)

        if self.walker is None:
            self.logger.error("Cannot spawn walker")
            exit("Cannot spawn walker")
        else:
            self.logger.info(f"successfully spawn walker {self.walker.id} at {self.walkerSpawnPoint.location.x, self.walkerSpawnPoint.location.y, self.walkerSpawnPoint.location.z}")
            self.logger.info(self.walker.get_control())
            
            # visualizer.trackOnTick(walker.id, {"life_time": 1})      
        
        # self.world.wait_for_tick() # otherwise we can get wrong agent location!
        self.tickOrWaitBeforeSimulation()


        config = {
            "visualizationForceLocation": carla.Location(x=-150.0, y=2.0, z=1.5),
            "visualizationInfoLocation": carla.Location(x=-155.0, y=0.0, z=1.5)
        }

        self.walkerAgent = self.pedFactory.createAgent(walker=self.walker, logLevel=self.logLevel, optionalFactors=self.optionalFactors, config=config)

        self.walkerAgent.setDestination(self.walkerDestination)
        self.visualizer.drawDestinationPoint(self.walkerDestination)

        # self.walkerAgent.updateLogLevel(logging.INFO)

        # attach actor manager

        pass

    
    def createVehicle(self, randomizeSpawnPoint=True):
        vehicleSpawnPoint = self.vehicleSpawnPoint
        # vehicleSpawnPoint = random.choice(self.mapManager.spawn_points)
        # randomize spawn point
        if randomizeSpawnPoint:
            currentWp = self.map.get_waypoint(vehicleSpawnPoint.location)
            distance = random.random() * 10 # 0 to 10 meter gap
            # vehicleSpawnPoint = currentWp.next(distance)[0].transform
            if np.random.choice([True, False]): # back for forward
                vehicleSpawnPoint = currentWp.next(distance)[0].transform
            else:
                vehicleSpawnPoint = currentWp.previous(distance)[0].transform
            vehicleSpawnPoint.location += carla.Location(z=1)

        self.vehicle = self.vehicleFactory.spawn(vehicleSpawnPoint)       
        if self.vehicle is None:
            self.logger.error("Cannot spawn vehicle")
            exit("Cannot spawn vehicle")
        else:
            self.logger.info(f"successfully spawn vehicle at {vehicleSpawnPoint.location.x, vehicleSpawnPoint.location.y, vehicleSpawnPoint.location.z}")

        self.tickOrWaitBeforeSimulation() # otherwise we can get wrong vehicle location!

        # self.vehicleAgent = self.vehicleFactory.createAgent(self.vehicle, target_speed=20, logLevel=logging.DEBUG)
        self.vehicleAgent = self.vehicleFactory.createBehaviorAgent(self.vehicle, behavior='normal', logLevel=logging.DEBUG)

        spawnXYLocation = carla.Location(x=vehicleSpawnPoint.location.x, y=vehicleSpawnPoint.location.y, z=0.001)

        # destination = self.getNextDestination(spawnXYLocation)
        destination = self.vehicleSetting.destination

        self.vehicleAgent.set_destination(destination, start_location=spawnXYLocation)
        self.visualizer.drawDestinationPoint(destination)

        pass


    def getNextDestination(self, currentLocation):

        return carla.Location(x=-132.862671, y=3, z=0.0)

        destination = random.choice(self.mapManager.spawn_points).location
        count = 1
        while destination.distance(currentLocation) < 5:
            destination = random.choice(self.mapManager.spawn_points).location
            count += 1
            if count > 5:
                self.logger.error(f"Cannot find a destination from {currentLocation}")
                raise Exception("Cannot find a destination")
        return destination

    def recreateVehicle(self):
        # destroy current one
        # self.simulator.removeOnTicker()
        self.logger.warn(f"Recreating vehicle")
        self.vehicleFactory.destroy(self.vehicle)
        self.vehicleAgent = None
        self.vehicle = None
        self.createVehicle()

    def resetWalker(self, sameOrigin=True):

        if sameOrigin == True:
            
            self.walkerAgent.reset(newStartPoint=self.walkerSetting.source)
            self.walkerAgent.setDestination(self.walkerSetting.destination)
            return 

        if self.walkerAgent.location.distance_2d(self.walkerSetting.source) < 1: # currently close to source
            self.walkerAgent.reset()
            self.walkerAgent.setDestination(self.walkerSetting.destination)
        else:
            self.walkerAgent.reset()
            self.walkerAgent.setDestination(self.walkerSetting.source)

    
    def createDynamicAgents(self):
        
        self.createVehicle()
        self.createWalker()
        pass

    def recreateDynamicAgents(self):
        # 1. recreated vehicle
        self.recreateVehicle()

        # 2. reset walker
        self.resetWalker(sameOrigin=True)

        pass
    
    
    #end region

    #region simulation

    def setupSimulator(self, episodic=False):
        """Must be called after all actors are created.

        Args:
            episodic (bool, optional): _description_. Defaults to False.
        """
        self.episodeNumber = 1 # updated when resetted

        onTickers = [self.visualizer.onTick, self.onTick] # onTick must be called before restart
        onEnders = [self.onEnd]
        terminalSignalers = [self.walkerAgent.isFinished]

        if episodic:
            self.simulator = EpisodeSimulator(self.client, terminalSignalers=terminalSignalers, onTickers=onTickers, onEnders=onEnders, simulationMode=self.simulationMode)
        else:
            onTickers.append(self.restart)
            self.simulator = Simulator(self.client, onTickers=onTickers, onEnders=onEnders, simulationMode=self.simulationMode)



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
        self.destoryActors()
        self.saveStats()

    def onTick(self, world_snapshot):

        self.episodeTimeStep += 1

        self.collectStats(world_snapshot)

        self.walkerAgent.onTickStart(world_snapshot)

        self.updateWalker(world_snapshot)
        self.updateVehicle(world_snapshot)

        # draw waypoints upto walker

        walkerWp = self.map.get_waypoint(self.walkerAgent.location).transform.location
        waypoints = Utils.getWaypointsToDestination(self.vehicle, walkerWp)
        self.visualizer.drawWaypoints(waypoints, color=(0, 0, 0), z=1, life_time=0.1)
        self.logger.info(f"Linear distance to pedestrian {self.walkerAgent.actorManager.distanceFromNearestOncomingVehicle()}")
        self.logger.info(f"Arc distance to pedestrian {Utils.getDistanceCoveredByWaypoints(waypoints)}")
    
    
    def updateWalker(self, world_snapshot):

        # print("updateWalker")

        if self.walkerAgent is None:
            self.logger.warn(f"No walker to update")
            return

        if self.walkerAgent.isFinished():
            self.logger.warn(f"Walker {self.walkerAgent.walker.id} reached destination")
            # self.logger.warn(f"Walker {self.walkerAgent.walker.id} reached destination. Going back")
            # if walkerAgent.destination == walkerSetting.destination:
            #     walkerAgent.set_destination(walkerSetting.source)
            #     visualizer.drawDestinationPoint(destination)
            # else:
            #     walkerAgent.set_destination(walkerSetting.destination)
            #     visualizer.drawDestinationPoint(destination)
            # return
        
        # print("canUpdate")
        # if self.walkerAgent.canUpdate():
        control = self.walkerAgent.calculateControl()
        # print("apply_control")
        self.walker.apply_control(control)
            
    def updateVehicle(self, world_snapshot):

        if self.vehicleAgent is None:
            self.logger.warn(f"No vehicle to update")
            return 

        if self.vehicleAgent.done():
            destination = random.choice(self.mapManager.spawn_points).location
            # self.vehicleAgent.set_destination(destination, self.vehicle.get_location())
            self.vehicleAgent.set_destination(destination)
            self.logger.info("The target has been reached, searching for another target")
            self.visualizer.drawDestinationPoint(destination)

        
        control = self.vehicleAgent.run_step()
        control.manual_gear_shift = False
        self.logger.info(control)
        self.vehicle.apply_control(control)
        pass

    def updateStatDataframe(self):
        # 1. make a dataframe from self.statDict
        df = pd.DataFrame.from_dict(self.statDict)
        # 2. merge it with the statDataframe
        self.statDataframe = pd.concat([self.statDataframe, df], ignore_index=True)
        # 3. clear self.statDict
        self.initStatDict()


    def initStatDict(self):

        if not self.stats:
            return
        # we will save trajectories of all the walkers and vehicles (location, speed, velocity). Time interval is not saved.

        # self.stats = pd.DataFrame(columns=['walker_trajectories'])

        # self.stats = {
        #     "walker_trajectories": {},
        # }

        # walkers = self.pedFactory.getWalkers()
        # vehicles  = self.vehicleFactory.getVehicles()
        
        # for walker in walkers

        # self.trajectories = pd.DataFrame(columns=["episode", "v_loc", "v_speed", "v_direction", "w_loc", "w_speed", "w_direction"])

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

        pass


    def saveStats(self):
        if not self.stats:
            return

        dateStr = date.today().strftime("%Y-%m-%d-%H-%M")
        statsPath = os.path.join(self.outputDir, f"{dateStr}-trajectories.csv")
        # df = pd.DataFrame.from_dict(self.statDict)
        # df.to_csv(statsPath, index=False)

        if len(self.statDataframe) == 0:
            self.logger.warn("Empty stats. It means no episode was completed in this run")
            return
        self.statDataframe.to_csv(statsPath, index=False)
        pass