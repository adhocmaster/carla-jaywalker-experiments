import carla
from abc import abstractmethod
from lib import ActorManager, ObstacleManager, Utils, NotImplementedInterface, InvalidParameter

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
    @abstractmethod
    def logger(self):
        pass

    
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

    def getNewControl(self):
        """Calculates new control by multiplying the resultant force by time delta
        """
        newVelocity = self.getNewVelocity()
        speed = newVelocity.length()
        direction = newVelocity.make_unit_vector()
        return carla.WalkerControl(
                direction = direction,
                speed = speed,
                jump = False
            )

    def getNewVelocity(self):
        oldVelocity = self.agent.getOldVelocity()
        dv = self.getRequiredChangeInVelocity()
        return oldVelocity + dv

    def getRequiredChangeInVelocity(self):
        timeDelta = Utils.getTimeDelta(self.world)
        if timeDelta < 0.001:
            raise InvalidParameter("Time delta too low for Pedestrian Planner")

        force = self.getResultantForce() # unit mass, so force == acceleration
        self.logger.info(f"Resultant force is {force}")
        self.logger.info(f"timeDelta is {timeDelta}")
        dv = force * timeDelta
        return dv

    @abstractmethod
    def getResultantForce(self):
        raise NotImplementedInterface("getResultantForce")

    @abstractmethod
    def calculateNextPedestrianState(self):
        raise NotImplementedInterface("calculateNextPedestrianState")

    @abstractmethod
    def calculateNextPedestrianState(self):
        raise NotImplementedInterface("calculateNextPedestrianState")

    @abstractmethod
    def calculateNextControl(self):
        raise NotImplementedInterface("calculateNextControl")

    @abstractmethod
    def calculateResultantForce(self):
        raise NotImplementedInterface("calculateResultantForce")

    @abstractmethod
    def getOncomingVehicles(self):
        raise NotImplementedInterface("getOncomingVehicles")

    @abstractmethod
    def getOncomingPedestrians(self):
        raise NotImplementedInterface("getOncomingPedestrians")

        
    @abstractmethod
    def getPrecedingPedestrians(self):
        raise NotImplementedInterface("getPrecedingPedestrians")

    @abstractmethod
    def getFollowingPedestrians(self):
        raise NotImplementedInterface("getFollowingPedestrians")