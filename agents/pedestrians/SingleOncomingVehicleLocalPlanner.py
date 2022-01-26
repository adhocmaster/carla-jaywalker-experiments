import carla
from .PedestrianPlanner import PedestrianPlanner

class SingleOncomingVehicleLocalPlanner(PedestrianPlanner):


    def __init__(self, vehicle: carla.Vehicle = None) -> None:
        self._vehicle = vehicle
        pass
    
    @property
    def vehicle(self):
        return self._vehicle

    def setVehicle(self, vehicle: carla.Vehicle) -> None:
        self._vehicle = vehicle
        pass


    def calculateNextPedestrianState(self):
        raise Exception("calculateNextPedestrianState")

    def calculateNextControl(self):
        raise Exception("calculateNextControl")


    def getOncomingVehicles(self):
        if self.vehicle is None:
            return []
        return [self.vehicle]


    def getOncomingPedestrians(self):
        raise Exception("getOncomingPedestrians")

        
    def getPrecedingPedestrians(self):
        raise Exception("getPrecedingPedestrians")


    def getFollowingPedestrians(self):
        raise Exception("getFollowingPedestrians")