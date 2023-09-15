import numpy as np
from agents.pedestrians.ForceModel import ForceModel
from agents.pedestrians.PedState import PedState
from agents.pedestrians.PedestrianAgent import PedestrianAgent
from agents.pedestrians.StateTransitionModel import StateTransitionModel
from agents.pedestrians.factors.InternalFactors import InternalFactors
from lib.InteractionUtils import InteractionUtils
from lib.ActorManager import ActorManager
from lib.ObstacleManager import ObstacleManager
from .SurvivalModel import SurvivalModel


class EvasiveStopModel(SurvivalModel, StateTransitionModel):
    def __init__(
        self,
        agent: PedestrianAgent,
        actorManager: ActorManager,
        obstacleManager: ObstacleManager,
        internalFactors: InternalFactors,
    ) -> None:

        super().__init__(
            agent, actorManager, obstacleManager, internalFactors=internalFactors
        )

        self._startVelocity = None
        self._maxActuationTime = None # seconds
        self._actuationTimeElapsed = None # seconds
        self._lastTick = None

        pass

    @property
    def name(self):
        return f"EvasiveStopModel #{self.agent.id}"
    
    def _reset(self):
        self._startVelocity = None
        self._maxActuationTime = None # seconds
        self._actuationTimeElapsed = None # seconds
        self._lastTick = None


    def getNewState(self):
        if self.agent.isFrozen() and self.canUnfreeze():
            # print(f"{self.name} unfreezing the pedestrian")
            return PedState.CROSSING
        elif self.agent.isCrossing() and self.canfreeze():
            # print(f"{self.name} freezing the pedestrian")
            return PedState.FROZEN

    def calculateForce(self):

        if not self.agent.isFrozen():
            self._reset()
            return None
        
        # TODO make a easing function
        if self._startVelocity is None:
            self._startVelocity = self.agent.velocity # TODO this is a bit incorrect 
            self._maxActuationTime = np.random.uniform(0.15, 0.5)
            self._actuationTimeElapsed = 0.0
            self._lastTick = self.agent.currentEpisodeTick
        
        if self._actuationTimeElapsed >= self._maxActuationTime:
            # hugeForce = -1 * (self._startVelocity / 0.001) # force will cause back and forth velocity
            return -1 * (self.agent.velocity / self.agent.timeDelta) # force will cause back and forth velocity
            # return None
        
        self._actuationTimeElapsed = self._actuationTimeElapsed + (self.agent.currentEpisodeTick - self._lastTick) * self.agent.timeDelta
        self._lastTick = self.agent.currentEpisodeTick
        # a linear easing function
        # return self._startVelocity * (1 - self._actuationTimeElapsed / self._maxActuationTime)
        # return -1 * (self._startVelocity / self._maxActuationTime)
        return -1 * (self._startVelocity / self._maxActuationTime)
        
    def canHardStop(self) -> bool:
        if not self.agent.isFrozen():
            return False
        if self._startVelocity is None:
            return False
        return self._actuationTimeElapsed >= self._maxActuationTime

    
    def canfreeze(self):
        """Can freeze only works if the TTC is less than 1.5 seconds

        Returns:
            _type_: _description_
        """
        # TTC = self.agent.ttcWithEgo() 
        # print(f"getting new state from evasive stop model, TTC: {TTC}")
        # if TTC is not None and TTC < 1.5:
        #     return True


        TG = self.agent.getAvailableTimeGapWithEgo()
        # print(f"canfreeze TG: {TG}")
        if not InteractionUtils.isOncoming(self.agent.walker, self.agent.egoVehicle):
            return False
        if TG is not None and TG < 1:
            return True
        
        return False


    def canUnfreeze(self):
        distance = self.agent.distanceFromEgo()
        if distance < 0.5:
            return False
        if self.canfreeze():
            return False
        return True