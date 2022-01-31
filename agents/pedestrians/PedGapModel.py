import carla
from lib import ActorManager, ObstacleManager, Utils, LoggerFactory
from .GapModel import GapModel
from .PedestrianAgent import PedestrianAgent
import random

class PedGapModel(GapModel):

    def __init__(self, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, factors = None) -> None:

        super().__init__(agent, actorManager, obstacleManager)
        self.name = f"PedGapModel #{agent.id}"
        self.logger = LoggerFactory.create(self.name)

        self.factors = factors
        self.initFactors()

        self.previousVehicleDistances = {} # stores distance to every vehicle on the last tick
        self.currentVehicleDistances = {} # stores distance to every vehicle in this tick

        pass

    
    def initFactors(self):
        if self.factors is None:
            self.factors = {}
        
        if "desired_gap" not in self.factors:
            self.factors["desired_gap"] = 10 
        
        pass

    @property
    def desiredGap(self):
        return self.factors["desired_gap"]

    def calculateForce(self):

        if self.agent.isCrossing():
            # random will not work. The force should be off while pedestrian is not on road
            # idea: if nearest waypoint is too far, that means pedestrian is not worried about on coming vehicle. But carla waypoint calculation is not reliable
            return Utils.createRandomVector(0, 0.5) # TODO implement force based on distance
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
            if self.isVehicleOncoming(vehicle, d):
                if d < minD:
                    minD = d
            self.currentVehicleDistances[vehicle] = d
        return minD

    
    def isVehicleOncoming(self, vehicle, currentDistance):
        if vehicle not in self.previousVehicleDistances:
            return False
        
        if self.previousVehicleDistances[vehicle] > currentDistance:
            return True
        
        return False