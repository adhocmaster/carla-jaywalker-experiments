

import carla
import numpy as np
from ..StateTransitionModel import StateTransitionModel
from ..PedState import PedState


class FreezingModel(StateTransitionModel):
    # create an init to declare counter variable 

    @property
    def name(self):
        return f"FreezingModel #{self.agent.id}"

    def getNewState(self):
        if self.agent.isFrozen() and self.canUnfreeze():
            return PedState.CROSSING
        elif self.agent.isCrossing() and self.canfreeze():
            return PedState.FROZEN

    
    def calculateForce(self):
        #TODO

        return None

    
    def canfreeze(self):
        #TODO
        conflictPoint = self.agent.getPredictedConflictPoint()
        # figure outwhere get predictedcofnlictp oint and potentially modify 
        if conflictPoint is None:
            return None
        return True


    def canUnfreeze(self):
        #TODO
        # decrease counter 
        # decide if we want to range from 0 - tcc or tg or just tcc or all at once since we want random
        return False

