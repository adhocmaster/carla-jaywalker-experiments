from turtle import distance
import carla
from abc import abstractmethod
from agents.pedestrians.PedUtils import PedUtils
from lib import ActorManager, ObstacleManager, Utils, LoggerFactory
from agents.pedestrians.PedestrianAgent import PedestrianAgent
from agents.pedestrians.factors import InternalFactors
from ..gap_models.GapModel import GapModel
import random

class AntiSurvivalTimeGapModel(GapModel):

    def __init__(self, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, internalFactors: InternalFactors) -> None:

        super().__init__(agent, actorManager, obstacleManager, internalFactors=internalFactors)
        self.logger = LoggerFactory.create(self.name)
        self.timeGap_error = 1

    @property
    def name(self):
        return f"AntiSurvivalTimeGapModel #{self.agent.id}"
    
    def calculateForce(self):
        pass

    def canCross(self):
        timeGap = self.getAvailableGap()
        if timeGap is None:
            self.timeGap_error = random.uniform(0.9, 1.1)
            return False

        relaxation_time, desired_speed = self.internalFactors["relaxation_time"], self.internalFactors["desired_speed"]
        distance_relaxation = (desired_speed/2) * relaxation_time
        time_to_cross = (5 - distance_relaxation)/desired_speed if (5 - distance_relaxation)/desired_speed > 0 else 0

        self.logger.info(f"Time gap is {timeGap} seconds")
        self.logger.info(f"Total time is {time_to_cross + relaxation_time} seconds")
        self.logger.info(f"TG error is {self.timeGap_error}")

        if time_to_cross + relaxation_time >= timeGap * self.timeGap_error:
            return True

        return False

    def getAvailableGap(self):
        return self.agent.getAvailableTimeGapWithClosestVehicle()

    def distanceFromOncomingVehicle(self):
        return self.actorManager.distanceFromNearestOncomingVehicle()


    @abstractmethod
    def p_go(self, gap):
        return 1

