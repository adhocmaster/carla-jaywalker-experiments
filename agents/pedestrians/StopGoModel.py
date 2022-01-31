import carla
from agents.pedestrians.PedState import PedState
from lib import ActorManager, ObstacleManager, Utils, LoggerFactory
from .ForceModel import ForceModel
from .GapModel import GapModel
from .PedestrianAgent import PedestrianAgent


class StopGoModel(ForceModel):
    
    def __init__(self, gapModel:GapModel, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, factors = None) -> None:

        super().__init__(agent, actorManager, obstacleManager)
        self.name = f"StopGoModel #{agent.id}"
        self.logger = LoggerFactory.create(self.name)

        self.gapModel = gapModel # it will use this model to decide whether to stop or go

        self.factors = factors
        self.initFactors()

        pass
    
    def initFactors(self):
        if self.factors is None:
            self.factors = {}
        
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

    