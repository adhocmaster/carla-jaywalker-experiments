

import carla
import numpy as np
from ..StateTransitionModel import StateTransitionModel
from ..PedState import PedState


class FreezingModel(StateTransitionModel):

    @property
    def name(self):
        return f"FreezingModel #{self.agent.id}"

    def getNewState(self):
        if self.agent.isFrozen() and self.canUnfreeze():
            return PedState.CROSSING
        elif self.agent.isCrossing() and self.canfreeze():
            return PedState.FROZEN

    
    def calculateForce(self):
        return None

    
    def canfreeze(self):
        return False


    def canUnfreeze(self):
        return False

