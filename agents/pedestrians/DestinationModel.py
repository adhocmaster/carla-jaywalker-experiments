import carla
import numpy as np
from lib import ActorManager, ObstacleManager, Utils
from .ForceModel import ForceModel
from .PedestrianAgent import PedestrianAgent
from agents.pedestrians.factors import InternalFactors
from .PedUtils import PedUtils
from .speed_models.SpeedModel import SpeedModel
from .destination import CrosswalkModel


class DestinationModel(ForceModel):

    def __init__(
        self, 
        agent: PedestrianAgent, 
        actorManager: ActorManager, 
        obstacleManager: ObstacleManager, 
        internalFactors: InternalFactors, 
        final_destination=None,
        debug=False
        ) -> None:

        super().__init__(
            agent, 
            actorManager, 
            obstacleManager, 
            internalFactors=internalFactors, 
            debug=debug
            )

        # self._source = source # source may not be current agent location
        self._finalDestination = final_destination
        self._nextDestination = final_destination

        self.skipForceTicks = 0
        self.skipForceTicksCounter = 0

        self.initFactors()

        self.speedModel: SpeedModel = None
        self.crosswalkModel: CrosswalkModel = None

        pass


    def initFactors(self):
        if "desired_speed" not in self.internalFactors:
            self.internalFactors["desired_speed"] = 2 

        if "relaxation_time" not in self.internalFactors:
            self.internalFactors["relaxation_time"] = 0.1 

        if "use_crosswalk_area_model" not in self.internalFactors:
            self.internalFactors["use_crosswalk_area_model"] = False
        
        pass

    @property
    def name(self):
        return f"DestinationModel {self.agent.id}"
        
    @property
    def nextDestination(self):
        if self.crosswalkModel is None:
            return self._nextDestination
        return self.crosswalkModel.getNextDestinationPoint()
    

    def addCrossWalkAreaModel(self):
        self.crosswalkModel = CrosswalkModel(
            agent = self.agent,
            source = self.agent.location,
            idealDestination = self._finalDestination,
            areaPolygon = None,
            goalLine = None,
            debug=self.debug
        )

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
        
        if self.internalFactors["use_crosswalk_area_model"]:
            if self.crosswalkModel is None:
                self.addCrossWalkAreaModel()
        
            

    
    def getDesiredVelocity(self) -> carla.Vector3D:

        speed = self.getDesiredSpeed()
        
        self.agent.logger.info(f"Desired speed is {speed}")

        velocity = self.getDesiredDirection() * speed 
        self.agent.logger.info(f"Desired velocity is {velocity}")

        return velocity

    def getDesiredSpeed(self) -> carla.Vector3D:
        if self.speedModel is None:
            speed = self.internalFactors["desired_speed"]
        else:
            speed = self.speedModel.desiredSpeed
        return speed


    def getDesiredDirection(self) -> carla.Vector3D:
        
        self.agent.logger.info(f"next destination is {self.nextDestination}")
        return Utils.getDirection(self.agent.feetLocation, self.nextDestination, ignoreZ=True)
        
        

    # def setNextDestination(self, destination):
    #     self._nextDestination = destination # TODO what we want to do is keep a destination queue and pop it to next destination when next destination is reached. 

    # def getDistanceToDestination(self):
    #     return Utils.getDistance(self.agent.feetLocation, self._nextDestination, ignoreZ=True)

    def getDistanceToNextDestination(self):
        return self.agent.getFeetLocation().distance(self.nextDestination)



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

        if self.crosswalkModel is not None:
            self._nextDestination = self.crosswalkModel.getNextDestinationPoint()

    
    def calculateForceForDesiredVelocity(self):

        """We changed the relationship between change in speed and relaxation time (made it linear so that the pedestrian can linearly increase the speed to the desired velocity)

        Returns:
            _type_: _description_
        """
        desiredVelocity = self.getDesiredVelocity()
        oldVelocity = self.agent.getOldVelocity()

        requiredChangeInVelocity = (desiredVelocity - oldVelocity)

        maxChangeInSpeed = desiredVelocity.length()
        requiredChangeInSpeed = requiredChangeInVelocity.length()

        relaxationTime = (requiredChangeInSpeed / maxChangeInSpeed) * self.internalFactors["relaxation_time"]
        
        return requiredChangeInVelocity / relaxationTime

    



