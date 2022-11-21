import logging
import random
from typing import List

import carla
from agents.pedestrians.factors import Factors
from agents.pedestrians.PedestrianFactory import PedestrianFactory
from agents.vehicles.VehicleFactory import VehicleFactory
from lib import (ClientUser, LoggerFactory, MapManager, MapNames, Geometry, LoggerFactory, RoadHelper,
                 NotImplementedInterface, SimulationMode,
                 SimulationVisualization)


class GameWorld(ClientUser):


    
    def __init__(
            self, 
            client: carla.Client,
            mapName=MapNames.circle_t_junctions, 
            outputDir:str = "logs", 
            logLevel=logging.INFO,
            stats=False
        ):

        super().__init__(client)

        self.mapName = mapName
        self.outputDir = outputDir
        self.logLevel = logLevel
        self.stats = stats
        self.time_delta = None
        self.mapManager = None
        self.visualizer = None

        self.initWorldSettingsAsynchronousMode()
        self.initVisualizer()

        self.logger = LoggerFactory.create("GameWorld", {"LOG_LEVEL": logLevel})
        self.walkers: List[carla.Walker] = []
        self.walkerAgents = []
        self.vehicleAgents = []
        self.pedFactory = PedestrianFactory(self.client, visualizer=self.visualizer, time_delta=self.time_delta)
        self.vehicleFactory = VehicleFactory(self.client, visualizer=self.visualizer)

        Geometry.visualizer = self.visualizer

    def configureMap(self):
        self.mapManager = MapManager(self.client)
        self.mapManager.load(self.mapName)
        
    def initWorldSettingsAsynchronousMode(self):
        self.configureMap()
        self.time_delta = 0.007
        settings = self.world.get_settings()
        settings.synchronous_mode = False # Enables synchronous mode
        settings.substepping = False
        settings.fixed_delta_seconds = self.time_delta
        self.world.apply_settings(settings)
        pass
    
    def initVisualizer(self):
        self.visualizer = SimulationVisualization(self.client, self.mapManager)
        self.visualizer.drawSpawnPoints(life_time=1.0)
        self.visualizer.drawSpectatorPoint()
        # self.visualizer.drawAllWaypoints(life_time=1.0)
        pass

    # region actors
    @property
    def worldVehicles(self) -> List[carla.Vehicle]:
        return list(self.worldActors.filter("vehicle*"))

    @property
    def playerVehicles(self) -> List[carla.Vehicle]:
        return [v for v in self.worldVehicles if v not in self.vehicles]

    @property
    def worldWalkers(self) -> List[carla.Walker]:
        return list(self.worldActors.filter("wallker*"))
    
    @property
    def vehicles(self) -> List[carla.Vehicle]:
        return self.vehicleFactory.getVehicles()

    # def addWalker(self, walker):
    #     self.walkers.append(walker)
    
    # def destroyWalker(self, walker):
    #     self.walkers.remove(walker)
    #     walker.destroy()

    

    # endregion

    # region lifecycle
    
    def destroy(self):
        self.walkers: List[carla.Walker] = []
        self.walkerAgents = []
        self.vehicleAgents = []
        self.vehicleFactory.reset()
        self.pedFactory.reset()
        pass

    # endregion

    # region dynamic generation

    # def getWaypointsNearPlayer(self, player: carla.Vehicle) -> List[carla.Waypoint]:

    #     playerWP = RoadHelper.getVehicleWP(self.map, player)
        
    #     v2vDistance = 5
        
    #     wps = []
    #     leftWP = RoadHelper.getWaypointOnTheLeft(self.map, playerWP)
    #     if leftWP is not None:
    #         wps.append(leftWP)
    #         wps.extend(RoadHelper.getWPsInFront(leftWP, v2vDistance, 3))
    #         wps.extend(RoadHelper.getWPsBehind(leftWP, v2vDistance, 3))

    #     rightWP = RoadHelper.getWaypointOnTheRight(self.map, playerWP)
    #     if rightWP is not None:
    #         wps.append(rightWP)
    #         wps.extend(RoadHelper.getWPsInFront(rightWP, v2vDistance, 3))
    #         wps.extend(RoadHelper.getWPsBehind(rightWP, v2vDistance, 3))
        
    #     playerLaneDistance = v2vDistance + player.get_velocity().length() * 3 # three second rule
    #     wps.extend(RoadHelper.getWPsInFront(playerWP, playerLaneDistance, 3))
    #     wps.extend(RoadHelper.getWPsBehind(playerWP, playerLaneDistance, 3))

    #     return wps
    

    def generateNPCVehicles(self, player: carla.Vehicle, nVehicles=3):
        wps = self.getWaypointsNearVehicle(self.map, player)
        self.logger.debug(f"Generated {len(wps)} waypoints for player {player.id}")
        if nVehicles > len(wps):
            raise Exception(f"number of vehicles is more than available way points")

        chosenWps = random.sample(wps, nVehicles)
        # print(chosenWps)

        # generatedVehicles = []

        # for wp in chosenWps:
        #     print(wp)
        #     try:
        #         generatedVehicles.append(self.vehicleFactory.spawn(wp.transform))
        #     except Exception as e:
        #         self.logger.warn(f"Cannot spawn vehicle at {wp.transform.location}")

        spawnPoints = [wp.transform for wp in wps]
        generatedVehicles = self.vehicleFactory.batchSpawn(spawnPoints)

        return generatedVehicles
        
        pass

    
    def generateNPCWalkers(self, player: carla.Vehicle, nPedestrians=3):

        # get forward way points
        # ray cast towards the right vector
        
        leftSpawnPoints, rightSpawnPoints = RoadHelper.getWalkerSpawnPointsInFront(self.world, player)
        chosenSpawnPoints = random.sample(leftSpawnPoints + rightSpawnPoints, nPedestrians)
        
        self.visualizer.drawSpawnPoints(spawn_points=chosenSpawnPoints)
        # return 
        
        optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE]
        config = {
            "visualizationForceLocation": carla.Location(x=-150.0, y=2.0, z=1.5),
            "visualizationInfoLocation": carla.Location(x=-155.0, y=0.0, z=1.5)
        }
        self.walkers, self.walkerAgents = self.pedFactory.batchSpawnWalkerAndAgent(
            chosenSpawnPoints,
            # logLevel=self.logLevel,
            logLevel=logging.ERROR,
            optionalFactors=optionalFactors,
            config=config
        )

        self.logger.info("created walkers and agents. Setting destinations")
        # return
        for walkerAgent in self.walkerAgents:
            # self.visualizer.drawPoint(walkerAgent.location, size=0.2, life_time=5.0)
            dest = Geometry.findClosestSidewalkLocationOnTheOtherSide(
                world=self.world,
                source=walkerAgent.location,
                scanRadius=20 # TODO: find road width and use that + 5 as a radius
            )
            assert dest is not None
            walkerAgent.setDestination(dest)


        



    # endregion

    # region static generation

    # endregion
    