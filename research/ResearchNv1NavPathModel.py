import numpy as np
import random
import carla
from agents.pedestrians.soft import *
from lib import SimulationMode
from lib.MapManager import MapNames
from lib.utils import Utils
from research.ResearchActors import WalkerActor
from research.ResearchNv1 import ResearchNv1
from settings.SourceDestinationPair import SourceDestinationPair


class ResearchNv1NavPathModel(ResearchNv1):
    
    
    def __init__(self, 
                 client: carla.Client, 
                 mapName=MapNames.circle_t_junctions, 
                 logLevel="INFO", 
                 outputDir:str = "logs", 
                 simulationMode = SimulationMode.ASYNCHRONOUS,
                 settingsId = "setting1",
                 stats=False,
                 record=False,
                 ignoreStatsSteps=0,
                 maxStepsPerCrossing=200,
                 navPathFilePath="data/navpath/nav_path_straight_road_group.json",
                 scenario = "psi-0048",
                 ):

        super().__init__(
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
        
        self.name = "ResearchNv1NavPathModel"

        self.scenario = scenario
        self.navPathFilePath = navPathFilePath

        self.vehicleLagForInitialization = 10.0
        pass
        
    @property
    def navPaths(self) -> NavPath:
        if hasattr(self, "_navPaths") is False or self._navPaths is None:
            self._navPaths = self.settingsManager.getNavPath(self.navPathFilePath, self.scenario)

        return self._navPaths
    
    def createWalker(self, navPath: NavPath):
        
        walkerSettings = self.createWalkerSettings(navPath)
        self.logger.warn(f"walkerSettings: {walkerSettings}")

        walker, walkerAgent = super().createWalker(walkerSettings)

        walkerAgent.setEgoVehicle(self.vehicle)
        walkerAgent.setNavPath(navPath, startFromSidewalk=False, endInSidewalk=True, vehicleLagForInitialization=self.vehicleLagForInitialization)

        self.walkerActors.append(
            WalkerActor(
                carlaActor=walker,
                agent=walkerAgent,
                settings=walkerSettings
            )
        )

        pass
    def createWalkers(self):
        for navPath in self.navPaths:
            self.createWalker(navPath)
        pass


    def createWalkerSettings(self, navPath: NavPath) -> SourceDestinationPair:
        vehicleSettings = self.getVehicleSetting()
        vehicleWp = self.map.get_waypoint(vehicleSettings.source, project_to_road=True, lane_type=carla.LaneType.Driving)
        futureVWPs = vehicleWp.next(navPath.path[0].distanceToInitialEgo + self.vehicleLagForInitialization)
        if len(futureVWPs) > 1:
            raise Exception("More than one possible waypoint for pedestrian spawn point")
        
        futureVWP = futureVWPs[0]
        self.logger.warn(f"futureVWP.lane_id: {futureVWP.lane_id}")
        navPoint = navPath.path[0]
        pedRequiredLaneId = navPoint.laneId

        adjustedPedWp = self.getLaneWpWrtVehicle(futureVWP, pedRequiredLaneId)

        ## TODO section adjustment

        ## Source and destination estimation
        leftSidewalk, rightSidewalk = Utils.getSideWalks(self.world, futureVWP) # with respect to the vehicle
        
        destination = leftSidewalk.location
        if navPath.direction == Direction.LR:
            destination = rightSidewalk.location
        
        source = adjustedPedWp.transform.location



        # add some randomness in the source further from destination
        destToSource = (source - destination).make_unit_vector()
        source = source + destToSource * np.random.uniform(0.5, 1.0)


        return SourceDestinationPair(
            source=carla.Location(source.x, source.y, z=0.5),
            destination=carla.Location(destination.x, destination.y, z=0.1),
        )
        
        

    
    def getLaneWpWrtVehicle(self, vehicleWp: carla.Waypoint, relativeLaneId: int) -> carla.Waypoint:
        """finds a waypoint at the relativeLaneId offset from the vehicle in lateral axis

        Args:
            vehicleWp (carla.Waypoint): _description_
            relativeLaneId (int): _description_

        Raises:
            Exception: _description_
            Exception: _description_

        Returns:
            carla.Waypoint: _description_
        """
        
        currWp = vehicleWp
        while(relativeLaneId > 0):
            currWp = vehicleWp.get_right_lane()
            if currWp is None:
                raise Exception("No right lane")
            relativeLaneId -= 1
        while(relativeLaneId < 0):
            currWp = vehicleWp.get_left_lane()
            if currWp is None:
                raise Exception("No left lane")
            relativeLaneId += 1
        
        return currWp
        # if vehicleWp.lane_id > 0:
        #     currWp = vehicleWp
        #     while(relativeLaneId > 0):
        #         currWp = vehicleWp.get_right_lane()
        #         relativeLaneId -= 1
        #     while(relativeLaneId < 0):
        #         currWp = vehicleWp.get_left_lane()
        #         relativeLaneId += 1
        # else:
        #     currWp = vehicleWp
        #     while(relativeLaneId > 0):
        #         currWp = vehicleWp.get_left_lane()
        #         relativeLaneId -= 1
        #     while(relativeLaneId < 0):
        #         currWp = vehicleWp.get_right_lane()
        #         relativeLaneId += 1

    
    def resetWalkers(self):
        self.createWalkers()
        pass

    
    def createVehicle(self, randomizeSpawnPoint=False):
        
        # meanSpeed = (self.navPath.egoConfiguration.egoSpeedStart + self.navPath.egoConfiguration.egoSpeedEnd) / 2
        # sd = 0.1
        # maxSpeed = np.random.normal(meanSpeed, sd) 
        maxSpeed = np.random.uniform(self.navPaths[0].egoConfiguration.egoSpeedStart, self.navPaths[0].egoConfiguration.egoSpeedEnd)
        self.vehicle, self.vehicleAgent = super(ResearchNv1, self).createVehicle(self.getVehicleSetting(), maxSpeed=maxSpeed, randomizeSpawnPoint=randomizeSpawnPoint)