import carla
from abc import abstractmethod
from lib import ActorManager, ObstacleManager, Utils

class PedestrianPlanner:
    """A planner has the state of the world, state of the pedestrian, and factors of the pedestrian. It does not plan any path or trajectory. 
    It's whole job is to send required states to factor models, get the force and state of the pedestrian. Apply the force and state in the world.
    """

    def __init__(self, agent) -> None:
        self._agent = agent
        self._world = agent.walker.get_world()
        self._map = self.world.get_map()
        self.actorManager = ActorManager(agent.walker)
        self.obstacleManager = ObstacleManager(agent.walker)
        self._destination = None
        pass

    @property
    def agent(self):
        return self._agent

    @property
    def world(self):
        return self._world

    @property
    def map(self):
        return self._map

    
    @property
    def destination(self):
        return self._destination

    def setDestination(self, destination):
        self._destination = destination

    
    def done(self):
        if self.getDistanceToDestination() < 0.1:
            return True
        return False
            
    def getDistanceToDestination(self):
        return Utils.getDistance(self.agent.feetLocation, self._destination, ignoreZ=True)

    def getDesiredDirection(self):
        return Utils.getDirection(self.agent.feetLocation, self._destination, ignoreZ=True)

    @abstractmethod
    def calculateNextPedestrianState(self):
        raise Exception("calculateNextPedestrianState")

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