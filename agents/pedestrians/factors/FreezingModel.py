

import carla
import numpy as np
from ..StateTransitionModel import StateTransitionModel
from ..PedState import PedState
import random


class FreezingModel(StateTransitionModel):
    # create an init to declare counter variable 

     def __init__(self, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, internalFactors: InternalFactors, final_destination=None) -> None:

        super().__init__(agent, actorManager, obstacleManager, internalFactors=internalFactors)

        # self.haveSafeDestination = False # This is a sequential model. There are some stuff to do at start, and some stuff to do at end.
        # self._destination = None
        self.counter = 0
        self.unfreezePeriod = 0
        #TG = self.agent.getAvailableTimeGapWithClosestVehicle()
        pass
    
    @property
    def name(self):
        return f"FreezingModel #{self.agent.id}"

    def getNewState(self):
        if self.agent.isFrozen() and self.canUnfreeze():
            return PedState.CROSSING
        elif self.agent.isCrossing() and self.canfreeze():
            return PedState.FROZEN

    
    def calculateForce(self):
        while (True):
            self.counter += 1000
        #TODO
        return None

    
    def canfreeze(self):
        #TODO
        conflictPoint = self.agent.getPredictedConflictPoint()
        if conflictPoint is None:
            return None
        return True


    def canUnfreeze(self):
        TTX = PedUtils.timeToCrossNearestLane(self.map, self.agent.location, self.agent._localPlanner.getDestinationModel().getDesiredSpeed())
        self.agent.logger.info(f"TG:  {TG} and TTX: {TTX}")
        self.counter -= 1000
        self.unfreezePeriod = random.randint()
        #TODO
        # decrease counter 
        # decide if we want to range from 0 - tcc or tg or just tcc or all at once since we want random
        return False

