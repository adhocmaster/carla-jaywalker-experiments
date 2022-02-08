from turtle import distance
import carla
from abc import abstractmethod
from agents.pedestrians.PedUtils import PedUtils
from lib import ActorManager, ObstacleManager, Utils, LoggerFactory
from agents.pedestrians.PedestrianAgent import PedestrianAgent
from agents.pedestrians.factors import InternalFactors
from lib import NotImplementedInterface
from .GapModel import GapModel
import numpy as np

class TimeGapModel(GapModel):

    def __init__(self, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, internalFactors: InternalFactors) -> None:

        super().__init__(agent, actorManager, obstacleManager, internalFactors=internalFactors)
        self.logger = LoggerFactory.create(self.name)
        # self.initFactors()

        pass

    @property
    def name(self):
        return f"TimeGapModel #{self.agent.id}"
    
    # def initFactors(self):

    #     pass

    def canCross(self):
        riskLevel = self.internalFactors["risk_level"]
        if riskLevel == "extreme":
            return True

        timeGap = self.getAvailableGap()

        self.logger.info(f"Time gap is {timeGap} seconds")
        if timeGap is None:
            return True
            
        p_go = self.p_go(timeGap)

        if riskLevel == "cautious":
            p_go = 0.8 * p_go

        if riskLevel == "risky":
            p_go = p_go * 2

        if p_go > 0.85:
            return True

        return np.random.choice([True, False], p=[p_go, 1-p_go])



    def getAvailableGap(self):
        return self.agent.getAvailableTimeGapWithClosestVehicle()


    @abstractmethod
    def p_go(self, gap):
        raise NotImplementedInterface("getGoProbability")

    # @abstractmethod
    # def getCriticalGap(self):
    #     raise NotImplementedInterface("getCriticalGap")

    # @abstractmethod
    # def getAvailableGap(self):
    #     raise NotImplementedInterface("getAvailableGap")

