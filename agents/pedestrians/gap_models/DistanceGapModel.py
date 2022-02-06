import carla
from agents.pedestrians.factors import InternalFactors
from lib import ActorManager, ObstacleManager, Utils, LoggerFactory
from .GapModel import GapModel
from agents.pedestrians.PedestrianAgent import PedestrianAgent

class DistanceGapModel(GapModel):

    def __init__(self, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, internalFactors: InternalFactors) -> None:

        super().__init__(agent, actorManager, obstacleManager, internalFactors=internalFactors)
        self.name = f"DistanceGapModel #{agent.id}"
        self.logger = LoggerFactory.create(self.name)
        self.initFactors()

        pass


    @property
    def name(self):
        return f"BrewerGapModel {self.agent.id}"
    
    def initFactors(self):
        pass

    @property
    def desiredGap(self):
        return self.internalFactors["desired_distance_gap"]

    def calculateForce(self):

        if self.agent.isCrossing():

            distanceOncoming = self.distanceFromOncomingVehicle()
            if distanceOncoming is not None:
                # random will not work. The force should be off while pedestrian is not on road
                # idea: if nearest waypoint is too far, that means pedestrian is not worried about on coming vehicle. But carla waypoint calculation is not reliable
                return Utils.createRandomVector(0, 0.5) # TODO implement force based on distance
                
        return carla.Vector3D() # in othe states this model does not produce force

    
    def canCross(self):

        if self.agent.isCrossing():
            True
        
        d = self.distanceFromOncomingVehicle()
        if d is None:
            return True

        # TODO implement the actual gap model. This is very straight forward
        if d > self.desiredGap:
            return True

        self.logger.info(f"Cannot cross as distance distance to oncoming vehicle {d} <= {self.desiredGap}")
        return False

    
    def distanceFromOncomingVehicle(self):
        return self.actorManager.distanceFromNearestOncomingVehicle()