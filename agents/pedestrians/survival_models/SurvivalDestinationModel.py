from sys import prefix
import carla
import numpy as np
from lib import ActorManager, ObstacleManager, Utils
from ..ForceModel import ForceModel
from ..PedestrianAgent import PedestrianAgent
from agents.pedestrians.factors import InternalFactors
from ..PedUtils import PedUtils
from .SurvivalModel import SurvivalModel
from ..PedState import PedState


class SurvivalDestinationModel(ForceModel, SurvivalModel):
    """This model finds a safe zone for the pedestrian and moves them there quickly. Planner has the history of last positions. Use this model in survival state only

    """

    def __init__(self, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, internalFactors: InternalFactors, final_destination=None) -> None:

        super().__init__(agent, actorManager, obstacleManager, internalFactors=internalFactors)

        self.haveSafeDestination = False # This is a sequential model. There are some stuff to do at start, and some stuff to do at end.
        self._destination = None

        pass


    @property
    def name(self):
        return f"SurvivalModel {self.agent.id}"

    
    def canSwitchToCrossing(self, TG, TTX):
        
        # 1. return to crossing is safe destination is reached
        if self.agent.isSurviving():
            if self.agent.location.distance_2d(self._destination) < 0.001:
                self._destination = None
                self.haveSafeDestination = False
                return True

            if TG is None or TG == 0:
                return True
            
            # diff = TG - TTX # may be too far
            # self.agent.logger.info(f"TG:  {TG} and TTX: {TTX}")
            # self.agent.logger.info(f"difference between TG and TTX: {diff}")
            # if diff > self.internalFactors["threshold_ttc_survival_state"]:
            #     return True
            # if diff < 0: # means vehicle will cross first
            #     if diff > -1:
            #         return True
            # elif diff > self.internalFactors["threshold_ttc_survival_state"]:
            #     return True

        return False

    def getNewState(self):

        TG = self.agent.getAvailableTimeGapWithClosestVehicle()
        TTX = PedUtils.timeToCrossNearestLane(self.map, self.agent.location, self.agent._localPlanner.getDestinationModel().getDesiredSpeed())

        # 1. return to crossing is safe destination is reached or vehicle stoppped
        if self.canSwitchToCrossing(TG, TTX):
            return PedState.CROSSING

        # 2. any other state means, we need to reset the safe destination
        if self.agent.isSurviving() == False:
            self.haveSafeDestination = False
        
        # 3. no survival state if the current state is not crossing
        if self.agent.isCrossing() == False: # wer change state only when crossing
            return None

        self.agent.logger.info(f"Collecting state from {self.name}")

        # 4. Switch to survival mode if close to a collision
        conflictPoint = self.agent.getPredictedConflictPoint()
        if conflictPoint is None:
            return None

        
        diff = TG - TTX # may be too far
        self.agent.logger.info(f"TG:  {TG} and TTX: {TTX}")
        self.agent.logger.info(f"difference between TG and TTX: {diff}")

        if diff < 0: # means vehicle will cross first
            if diff < -2:
                return PedState.SURVIVAL
        elif diff < self.internalFactors["threshold_ttc_survival_state"]:
            return PedState.SURVIVAL

        return None


    def calculateForce(self):
        if self.agent.isSurviving() == False:
            return None
        
        if self.haveSafeDestination == False:
            # this is the first step
            self.findSafeDestination()
        
        self.agent.logger.info(f"Survival desitnation = {self._destination}")
        # do normal calculations
        # force is now the same as the destination model.

        direction = Utils.getDirection2D(self.agent.location, self._destination)
        speed = self.internalFactors["desired_speed"] 
        desiredVelocity = direction * speed
        
        oldVelocity = self.agent.getOldVelocity()

        force = (desiredVelocity - oldVelocity) / (self.internalFactors["relaxation_time"] * 0.1)

        # stopping case
        if self.agent.location.distance_2d(self._destination) < 0.5:
            force = force * -100 # a huge negative force to stop fast

        return force

        # now 

    
    def findSafeDestination(self):

        # find a location from previous locations that is 5-10 meter back.

        prevLocations = self.agent.previousLocations

        if len(prevLocations) == 0:
            raise Exception(f"No previous locations to safely go to")

        
        # we find a point in the direction firstLocation - currentLocation * min distance

        self.agent.logger.info(prevLocations)

        maxDistanceBack =  self.internalFactors["survival_safety_distance"]
        # we subtract the distance to next way point to 
        nearestWp, dToWp = PedUtils.getNearestDrivingWayPointAndDistance(self.map, self.agent.location)
        distance = min(maxDistanceBack, maxDistanceBack / dToWp)


        backwardVector = prevLocations[-1] - self.agent.location
        if backwardVector.length() < 0.000001:
            # raise Exception(f"No backward vector")
            self.agent.logger.info(f"No backward vector. setting to current location")
            safeDestination = self.agent.location
        else:
            safeDestination = self.agent.location + backwardVector.make_unit_vector() * distance
        
        
        self._destination = safeDestination
        self.agent.logger.info(safeDestination)

        # if len(prevLocations) == 1:
        #     self._destination = prevLocations[0]
        #     return

        # lastLocation = prevLocations[0]
        # firstLocation = prevLocations[-1]

        # distanceToDestination = lastLocation.distance_2d(firstLocation)

        # if distanceToDestination < self.internalFactors["survival_safety_distance"]:

        #     self._destination = firstLocation
        #     self.agent.logger.info(f"Distance to safe destination: {self.agent.location.distance_2d(self._destination)}")
        #     return

        # # TODO improve this
        # self._destination = firstLocation

        self.agent.logger.info(f"Distance to safe destination: {self.agent.location.distance_2d(self._destination)}")
        self.agent.logger.info(f"Distance to safe destination: {self.agent.location.distance_2d(self._destination)}")

        self.haveSafeDestination = True
