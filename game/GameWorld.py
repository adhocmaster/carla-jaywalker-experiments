from lib.ClientUser import ClientUser
import carla
from typing import List

from agents.vehicles.VehicleFactory import VehicleFactory

class GameWorld(ClientUser):


    
    def __init__(self, client):
        super().__init__(client)
        self.walkers: List[carla.Walker] = []
        self.walkerAgents = []
        self.vehicles: List[carla.Vehicle] = []
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
    
    def addWalker(self, walker):
        self.walkers.append(walker)
    
    def destroyWalker(self, walker):
        self.walkers.remove(walker)
        walker.destroy()

    def addVehicle(self, vehicle):
        self.vehicles.append(vehicle)
    
    def destroyVehicle(self, vehicle):
        self.vehicles.remove(vehicle)
        vehicle.destroy()
    

    # endregion

    # region dynamic generation

    def getWaypointsNearPlayer(self, player: carla.Vehicle) -> List[carla.Waypoint]:
        playerLocation = player.get_location()
        playerWp = self.map.get_waypoint(
            playerLocation,
            project_to_road=True
            )
        
        playerTransform = player.get_transform()
        forwardVector = playerTransform.get_forward_vector()
        rightVector = playerTransform.get_right_vector()

        pointOnRight = rightVector * 3 + playerLocation
        rightWp = self.map.get_waypoint(
            pointOnRight,
            project_to_road=True
        )
        
        # find way points on a circle at 10 meter radius and then extend way points?


    # endregion

    # region static generation
    # endregion
    