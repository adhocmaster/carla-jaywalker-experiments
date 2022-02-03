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


    def canCross(self):
        timeGap = self.getAvailableGap()
        p_go = self.getGoProbability()
        agressionLevel = self.internalFactors["aggression_level"]

        if agressionLevel == "normal":
            return np.random.choice([True, False], p_go)

        if agressionLevel == "cautious":
            return np.random.choice([True, False], 0.8 * p_go)

        if agressionLevel == "risky":
            return np.random.choice([True, False], p_go * 2)



    def getAvailableGap(self):
        distance = self.actorManager.distanceFromNearestOncomingVehicle()
        # time gap = time taken for the oncoming vehicle to reach


    @abstractmethod
    def p_go(self):
        raise NotImplementedInterface("getGoProbability")

    # @abstractmethod
    # def getCriticalGap(self):
    #     raise NotImplementedInterface("getCriticalGap")

    # @abstractmethod
    # def getAvailableGap(self):
    #     raise NotImplementedInterface("getAvailableGap")

