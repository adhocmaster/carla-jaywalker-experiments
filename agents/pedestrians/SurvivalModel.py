from sys import prefix
import carla
import numpy as np
from lib import ActorManager, ObstacleManager, Utils
from .ForceModel import ForceModel
from .PedestrianAgent import PedestrianAgent
from agents.pedestrians.factors import InternalFactors
from .PedUtils import PedUtils


class SurvivalModel(ForceModel):
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

        
    def getNewState(self):
        if self.agent.isSurviving() == False:
            self.started = False
            return None

        self.agent.logger.info(f"Collecting state from {self.name}")



    def calculateForce(self):
        if self.agent.isSurviving() == False:
            return None
        
        if self.haveSafeDestination == False:
            # this is the first step
            self.findSafeDestination()
        
        # do normal calculations
        # force is now the same as the destination model.

    
    def findSafeDestination(self):

        # find a location from previous locations that is 5-10 meter back.

        prevLocations = self.agent.previousLocations

        if len(prevLocations) == 0:
            raise Exception(f"No previous locations to safely go to")

        if len(prevLocations) == 1:
            self._destination = prevLocations[0]
            return

        lastLocation = prevLocations[0]
        firstLocation = prevLocations[-1]

        distanceToDestination = lastLocation.distance_2d(firstLocation)

        if distanceToDestination < self.internalFactors["survival_safety_distance"]:
            self._destination = firstLocation
            return

        

        self.haveSafeDestination = True
