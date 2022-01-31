import carla
from lib import ActorManager, ObstacleManager, Utils, LoggerFactory
from .ForceModel import ForceModel
from .PedestrianAgent import PedestrianAgent
import random

class PedGapModel(ForceModel):

    def __init__(self, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, factors = None) -> None:

        super().__init__(agent, actorManager, obstacleManager)
        self.name = f"PedGapModel #{agent.id}"
        self.logger = LoggerFactory.create(self.name)

        self.factors = factors
        self.initFactors()

        pass

    
    def initFactors(self):
        if self.factors is None:
            self.factors = {}
        
        if "desired_gap" not in self.factors:
            self.factors["desired_gap"] = 20 
        
        pass

    @property
    def desiredGap(self):
        return self.factors["desired_gap"]

    def calculateForce(self):

        if self.agent.isCrossing():
            return carla.Vector3D() + random.randint(0, 2) # TODO implement force based on distance
        return carla.Vector3D() # in othe states this model does not produce force

    
    def canCross(self):

        if self.agent.isCrossing():
            True
        
        d = self.distanceFromOncomingVehicle()
        # TODO implement the actual gap model. This is very straight forward
        self.logger.info(f"Min distance to any vehicle is {d}")
        if d > self.desiredGap:
            return True
        return False

    
    def distanceFromOncomingVehicle(self):
        # TODO we are now just measuring distance from all actors
        vehicles = self.actorManager.getVehicles()
        minD = 999999
        for vehicle in vehicles:
            d = vehicle.get_location().distance_2d(self.agent.location)
            if d < minD:
                minD = d
        return minD
