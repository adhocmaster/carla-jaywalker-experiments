import carla
import numpy as np
from ..StateTransitionModel import StateTransitionModel
from lib import ActorManager, ObstacleManager, LoggerFactory, TooManyNewStates, Utils
from ..PedestrianAgent import PedestrianAgent
from ..PedState import PedState
from agents.pedestrians.factors import *
import random


class FreezingModel(StateTransitionModel):
    # create an init to declare counter variable 

    def __init__(self, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, internalFactors: InternalFactors, final_destination=None) -> None:
        # self.haveSafeDestination = False # This is a sequential model. There are some stuff to do at start, and some stuff to do at end.
        # self._destination = None
        super().__init__(agent, actorManager, obstacleManager, internalFactors=internalFactors)

        self._agent = agent
        self.counter = 0
        #self.TG = self.agent.getAvailableTimeGapWithClosestVehicle()
        self.unfreezePeriod = random.randint(0.0, 5.0)
        self.freezePeriod = random.randint(0.0, 1.0)
        pass
    
    @property
    def name(self):
        return f"FreezingModel #{self.agent.id}"

    def getNewState(self):
        if self.agent.isFrozen() and self.canUnfreeze():
            return PedState.CROSSING
        elif self.agent.isCrossing() and self.canfreeze():
            # frozen

            return PedState.FROZEN

    
    def calculateForce(self):
        if self.agent.isFrozen():
            # if we are frozen, we want the desired speed
            oldVelocity = self.agent.getOldVelocity()
            desiredVelocity = -1 * oldVelocity

            force = (desiredVelocity) / (self.internalFactors["relaxation_time"] * 0.1)
            # desired velocity to be zero since we want the homie to be frozen
            return force
        else:
            return None

    
    def canfreeze(self):

        #TODO
        conflictPoint = self.agent.getPredictedConflictPoint() # are there multiple conflict points? yes/
        # calculate the difference between the pedestrian position and conflict point
        if conflictPoint is None:
            return False
        
        return True


    def canUnfreeze(self):
        #self.agent.logger.info(f"TTX: {self.TTX}")
        if self.unfreezePeriod == 0:
            return True
        else:
            self.unfreezePeriod -= 0.001

        


        #TODO
        # decrease counter 
        # decide if we want to range from 0 - tcc or tg or just tcc or all at once since we want random
        return False

