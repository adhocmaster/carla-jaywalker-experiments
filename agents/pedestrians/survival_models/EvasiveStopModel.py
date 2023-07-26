from agents.pedestrians.ForceModel import ForceModel
from agents.pedestrians.PedState import PedState
from agents.pedestrians.PedestrianAgent import PedestrianAgent
from agents.pedestrians.StateTransitionModel import StateTransitionModel
from agents.pedestrians.factors.InternalFactors import InternalFactors
from lib.ActorManager import ActorManager
from lib.ObstacleManager import ObstacleManager
from .SurvivalModel import SurvivalModel


class EvasiveStopModel(ForceModel, SurvivalModel, StateTransitionModel):
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



        pass

    @property
    def name(self):
        return f"EvasiveStopModel #{self.agent.id}"

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