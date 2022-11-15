from lib.ClientUser import ClientUser
import carla
from typing import List

from agents.vehicles.VehicleFactory import VehicleFactory
from lib.RoadHelper import RoadHelper
import random
from lib.LoggerFactory import LoggerFactory
import logging

class GameWorld(ClientUser):


    
    def __init__(
        self, 
        client,
        logLevel=logging.INFO
        ):
        super().__init__(client)

        self.logger = LoggerFactory.create("GameWorld", {"LOG_LEVEL": logLevel})
        self.walkers: List[carla.Walker] = []
        self.walkerAgents = []
        self.vehicleAgents = []

        self.vehicleFactory = VehicleFactory(self.client)


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

    def addWalker(self, walker):
        self.walkers.append(walker)
    
    def destroyWalker(self, walker):
        self.walkers.remove(walker)
        walker.destroy()

    

    # endregion

    # region lifecycle
    
    def destroy(self):
        self.vehicleFactory.reset()
        pass

    # endregion

    # region dynamic generation

    def getWaypointsNearPlayer(self, player: carla.Vehicle) -> List[carla.Waypoint]:
        playerLocation = player.get_location()
        playerWP = self.map.get_waypoint(
            playerLocation,
            project_to_road=True
            )
        
        v2vDistance = 5
        
        wps = []
        leftWP = RoadHelper.getWaypointOnTheLeft(self.map, playerWP)
        if leftWP is not None:
            wps.append(leftWP)
            wps.extend(RoadHelper.getWPsInFront(leftWP, v2vDistance, 3))
            wps.extend(RoadHelper.getWPsBehind(leftWP, v2vDistance, 3))

        rightWP = RoadHelper.getWaypointOnTheRight(self.map, playerWP)
        if rightWP is not None:
            wps.append(rightWP)
            wps.extend(RoadHelper.getWPsInFront(rightWP, v2vDistance, 3))
            wps.extend(RoadHelper.getWPsBehind(rightWP, v2vDistance, 3))
        
        playerLaneDistance = v2vDistance + player.get_velocity().length() * 3 # three second rule
        wps.extend(RoadHelper.getWPsInFront(playerWP, playerLaneDistance, 3))
        wps.extend(RoadHelper.getWPsBehind(playerWP, playerLaneDistance, 3))

        return wps
    

    def generateNPCVehicles(self, player: carla.Vehicle, nVehicles=3):
        wps = self.getWaypointsNearPlayer(player)
        self.logger.debug(f"Generated {len(wps)} waypoints for player {player.id}")
        if nVehicles > len(wps):
            raise Exception(f"number of vehicles is more than available way points")

        chosenWps = random.sample(wps, nVehicles)
        print(chosenWps)

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



        



    # endregion

    # region static generation
    # endregion
    