import carla
from lib import ActorManager, ObstacleManager
from .ForceModel import ForceModel
from .PedestrianAgent import PedestrianAgent

class DestinationModel:

    def __init__(self, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, source, final_destination, factors = None) -> None:

        super().__init__(agent, actorManager, obstacleManager)

        self._source = source
        self._finalDestination = final_destination
        self._nextDestination = final_destination

        self.factors = factors

        pass

    
    def initFactors(self):
        if self.factors is None:
            self.factors = {}
        
        if "desired_speed" not in self.factors:
            self.factors["desired_speed"] = 2 

        if "relaxation_time" not in self.factors:
            self.factors["relaxation_time"] = 2 
        
        pass

    
    def getDesiredVelocity(self) -> carla.Vector3D:
        return self.getDesiredDirection() * self.factors["desired_speed"] 


    def getDesiredDirection(self) -> carla.Vector3D:
        currentLocation = self.agent.getFeetLocation()
        distance = self.getDistanceToNextDestination()

        direction = carla.Vector3D(
            x = (self._nextDestination.x - currentLocation.x) / distance,
            y = (self._nextDestination.y - currentLocation.y) / distance,
            z = (self._nextDestination.z - currentLocation.z) / distance
        )
        return direction

    def getDistanceToNextDestination(self):
        return self.agent.getFeetLocation().distance(self._nextDestination)


    def calculateForce(self):
        return self.calculateForceForDesiredVelocity()
    
    def calculateForceForDesiredVelocity(self):
        desiredVelocity = self.getDesiredVelocity()
        oldVelocity = self.agent.getOldVelocity()

        return (desiredVelocity - oldVelocity) / self.factors["relaxation_time"]



