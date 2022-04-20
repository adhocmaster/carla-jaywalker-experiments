import carla
import numpy as np
from lib import ActorManager, ObstacleManager, Utils
from .ForceModel import ForceModel
from .PedestrianAgent import PedestrianAgent
from agents.pedestrians.factors import InternalFactors
from .PedUtils import PedUtils
from .speed_models.SpeedModel import SpeedModel


class DestinationModel(ForceModel):

    def __init__(self, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, internalFactors: InternalFactors, final_destination=None) -> None:

        super().__init__(agent, actorManager, obstacleManager, internalFactors=internalFactors)

        # self._source = source # source may not be current agent location
        self._finalDestination = final_destination
        self._nextDestination = final_destination

        self.skipForceTicks = 0
        self.skipForceTicksCounter = 0

        self.initFactors()

        self.speedModel: SpeedModel = None

        pass



    @property
    def name(self):
        return f"DestinationModel {self.agent.id}"
    
    def initFactors(self):
        if "desired_speed" not in self.internalFactors:
            self.internalFactors["desired_speed"] = 2 

        if "relaxation_time" not in self.internalFactors:
            self.internalFactors["relaxation_time"] = 0.1 
        
        pass

    def applySpeedModel(self, speedModel):
        self.speedModel = speedModel

    # def skipNextTicks(self, n):
    #     """We can skip n next ticks

    #     Args:
    #         n ([type]): [description]
    #     """
    #     self.skipForceTicks = n
    #     self.skipForceTicksCounter = 0

    # def needSkip(self):
    #     """One time skip counter

    #     Returns:
    #         [type]: [description]
    #     """
    #     if self.skipForceTicks == 0:
    #         return False
        
    #     if self.skipForceTicksCounter > self.skipForceTicks:
    #         self.skipForceTicksCounter = 0
    #         self.skipForceTicks = 0
    #         return False
        
    #     self.skipForceTicksCounter += 1
    #     return True

    
    def setFinalDestination(self, destination):
        """
        This method creates a list of waypoints between a starting and ending location,
        based on the route returned by the global router, and adds it to the local planner.
        If no starting location is passed, the vehicle local planner's target location is chosen,
        which corresponds (by default), to a location about 5 meters in front of the vehicle.

            :param end_location (carla.Location): final location of the route
            :param start_location (carla.Location): starting location of the route
        """
        
        self._finalDestination = destination
        # if self._nextDestination is None:
        #     self._nextDestination = destination
        self._nextDestination = destination # TODO what we want to do is keep a destination queue and pop it to next destination when next destination is reached. 
        
            
    def setNextDestination(self, destination):
        self._nextDestination = destination # TODO what we want to do is keep a destination queue and pop it to next destination when next destination is reached. 

    def getDistanceToDestination(self):
        return Utils.getDistance(self.agent.feetLocation, self._nextDestination, ignoreZ=True)

    
    def getDesiredVelocity(self) -> carla.Vector3D:

        if self.speedModel is None:
            speed = self.internalFactors["desired_speed"]
        else:
            speed = self.speedModel.desiredSpeed

        self.agent.logger.info(f"Desired speed is {speed}")

        return self.getDesiredDirection() * speed 

    def getDesiredSpeed(self) -> carla.Vector3D:
        return self.internalFactors["desired_speed"] 


    def getDesiredDirection(self) -> carla.Vector3D:
        return Utils.getDirection(self.agent.feetLocation, self._nextDestination, ignoreZ=True)
        
        

    def getDistanceToNextDestination(self):
        return self.agent.getFeetLocation().distance(self._nextDestination)


    def calculateForce(self):

        # return None
        if self.agent.isCrossing() == False:
            return None


        self.agent.logger.info(f"Collecting state from {self.name}")
        
        # if self.needSkip:
        #     return None

        self.calculateNextDestination()

        force = self.calculateForceForDesiredVelocity()

        # now clip force.
        
        return self.clipForce(force)



    def calculateNextDestination(self):


        # # First we check if we need to go back to origin.

        # TG = self.agent.getAvailableTimeGapWithClosestVehicle()
        
        # TTX = PedUtils.timeToCrossNearestLane(self.map, self.location, self._localPlanner.getDestinationModel().getDesiredSpeed())


        # if TG > TTX:
        #     # positive oncoming vehicle force
        # else:
        #     # negative oncoming vehicle force.


        # # last, check if next destination is reached, if so, set it to final destination

        if self._nextDestination.distance_2d(self.agent.location) < 0.1:
            self._nextDestination = self._finalDestination

    
    def calculateForceForDesiredVelocity(self):
        desiredVelocity = self.getDesiredVelocity()
        oldVelocity = self.agent.getOldVelocity()

        return (desiredVelocity - oldVelocity) / self.internalFactors["relaxation_time"]

    



