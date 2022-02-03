from turtle import distance
import carla
from abc import abstractmethod
from lib import ActorManager, ObstacleManager, Utils, LoggerFactory
from agents.pedestrians.PedestrianAgent import PedestrianAgent
from agents.pedestrians.factors import InternalFactors
from lib import NotImplementedInterface
from .GapModel import GapModel
import numpy as np

class TimeGapModel(GapModel):

    def __init__(self, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, internalFactors: InternalFactors) -> None:

        super().__init__(agent, actorManager, obstacleManager, internalFactors=internalFactors)
        self.name = f"TimeGapModel #{agent.id}"
        self.logger = LoggerFactory.create(self.name)
        self.initFactors()

        pass

    
    def initFactors(self):

        pass

    def canCross(self):
        timeGap = self.getAvailableGap()
        if timeGap is None:
            return True
            
        p_go = self.p_go(timeGap)
        agressionLevel = self.internalFactors["aggression_level"]

        if agressionLevel == "cautious":
            p_go = 0.8 * p_go

        if agressionLevel == "risky":
            p_go = p_go * 2

        return np.random.choice([True, False], p=[p_go, 1-p_go])



    def getAvailableGap(self):
        # distance = self.actorManager.distanceFromNearestOncomingVehicle()
        # time gap = time taken for the oncoming vehicle to reach + time to cross the lane.
        # TODO add 
        return self.actorManager.TTCNearestOncomingVehicle()


    @abstractmethod
    def p_go(self, gap):
        raise NotImplementedInterface("getGoProbability")

    # @abstractmethod
    # def getCriticalGap(self):
    #     raise NotImplementedInterface("getCriticalGap")

    # @abstractmethod
    # def getAvailableGap(self):
    #     raise NotImplementedInterface("getAvailableGap")

