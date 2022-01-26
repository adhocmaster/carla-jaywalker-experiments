import carla
from abc import abstractmethod

class PedestrianPlanner:
    """A planner has the state of the world, state of the pedestrian, and factors of the pedestrian. It does not plan any path or trajectory. 
    It's whole job is to send required states to factor models, get the force and state of the pedestrian. Apply the force and state in the world.
    """


    @abstractmethod
    def calculateNextPedestrianState(self):
        raise Exception("calculateNextPedestrianState")

    @abstractmethod
    def calculateNextControl(self):
        raise Exception("calculateNextControl")

    @abstractmethod
    def calculateResultantForce(self):
        raise Exception("calculateResultantForce")

    @abstractmethod
    def getOncomingVehicles(self):
        raise Exception("getOncomingVehicles")

    @abstractmethod
    def getOncomingPedestrians(self):
        raise Exception("getOncomingPedestrians")

        
    @abstractmethod
    def getPrecedingPedestrians(self):
        raise Exception("getPrecedingPedestrians")

    @abstractmethod
    def getFollowingPedestrians(self):
        raise Exception("getFollowingPedestrians")