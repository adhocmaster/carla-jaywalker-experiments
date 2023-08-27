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

        pass

    @property
    def name(self):
        return f"EvasiveStopModel #{self.agent.id}"

    def getNewState(self):
        # print(f"{self.name} getNewState the pedestrian")
        if self.agent.isFrozen() and self.canUnfreeze():
            # print(f"{self.name} unfreezing the pedestrian")
            return PedState.CROSSING
        elif self.agent.isCrossing() and self.canfreeze():
            # print(f"{self.name} freezing the pedestrian")
            return PedState.FROZEN

    def calculateForce(self):
        return None

    
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