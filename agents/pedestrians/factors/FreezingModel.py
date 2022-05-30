import carla
import numpy as np
from ..StateTransitionModel import StateTransitionModel
from lib import ActorManager, ObstacleManager, LoggerFactory, TooManyNewStates, Utils
from ..PedestrianAgent import PedestrianAgent
from ..PedState import PedState
from agents.pedestrians.factors import *
import random


class FreezingModel(StateTransitionModel):

    def __init__(self, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, internalFactors: InternalFactors, final_destination=None) -> None:
        # self.haveSafeDestination = False # This is a sequential model. There are some stuff to do at start, and some stuff to do at end.
        # self._destination = None
        super().__init__(agent, actorManager, obstacleManager, internalFactors=internalFactors)

        self._agent = agent
        #self.TTC = self.actorManager.pedPredictedTTCNearestOncomingVehicle()
        #self.TG = self.agent.getAvailableTimeGapWithClosestVehicle()
        self.unfreezePeriod = random.randint(8.0, 10)
        pass
    
    @property
    def name(self):
        return f"FreezingModel #{self.agent.id}"

    def getNewState(self):
        TTC = self.actorManager.pedPredictedTTCNearestOncomingVehicle()
        if self.agent.isFrozen() and self.canUnfreeze(TTC):
            return PedState.CROSSING
        elif self.agent.isCrossing() and self.canfreeze(TTC):
            # frozen
            return PedState.FROZEN
        
        # if we want to remain in the same state 
        return None 
    
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

    
    def canfreeze(self, TTC):
        # using TCC to calculate when the pedestrian can freeze
        # as the TTC decreases close to 2 seconds, we want to freeze
        # if TTC increases up to 10 seconds then we want to unfreeze
        if TTC != None:
            if TTC <= random.randint(1,3):
                return True
            if TTC > 10:
                return False
        
        # if TTC is None
        return False 

    def canUnfreeze(self, TTC):
        #self.agent.logger.info(f"TTX: {self.TTX}")
        if self.unfreezePeriod == 0  and (TTC == None or TTC > 12):
            return True
        else:
            if self.unfreezePeriod > 0:
                self.unfreezePeriod -= 0.5
        return False

