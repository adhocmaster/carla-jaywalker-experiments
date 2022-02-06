import carla
from agents.pedestrians.PedState import PedState
from lib import ActorManager, ObstacleManager, Utils, LoggerFactory
from .StateTransitionModel import StateTransitionModel
from .gap_models.GapModel import GapModel
from .PedestrianAgent import PedestrianAgent
from agents.pedestrians.factors import InternalFactors


class StopGoModel(StateTransitionModel):
    
    def __init__(self, gapModel:GapModel, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, 
                    internalFactors: InternalFactors) -> None:

        super().__init__(agent, actorManager, obstacleManager, internalFactors=internalFactors)
        # self.name = f"StopGoModel #{agent.id}"
        self.logger = LoggerFactory.create(self.name)

        self.gapModel = gapModel # it will use this model to decide whether to stop or go

        self.initFactors()

        pass

    @property
    def name(self):
        return f"StopGoModel #{self.agent.id}"
    
    def initFactors(self):        
        pass

    def calculateForce(self):
        return self.gapModel.calculateForce()

    
    def canCross(self):
        return self.gapModel.canCross()

    def getNewState(self):

        # if waiting and can cross, return crossing
        if self.agent.isWaiting():
            if self.canCross():
                return PedState.CROSSING

        return None 

    