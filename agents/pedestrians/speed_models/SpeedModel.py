from abc import abstractmethod
from agents.pedestrians.factors import InternalFactors
from lib import ActorManager, ObstacleManager

from lib.exceptions import NotImplementedInterface

class SpeedModel:

    def __init__(self, agent: any,  actorManager: ActorManager, obstacleManager: ObstacleManager,
                    internalFactors: InternalFactors) -> None:

        self._desiredSpeed = None
        self._minSpeed = None
        self._maxSpeed = None

        self.internalFactors = internalFactors

        self.initialize()

        pass


    @abstractmethod
    def initialize(self):
        raise NotImplementedInterface("initialize")

    @property
    def minSpeed(self):
        return self._minSpeed

    @property
    def maxSpeed(self):
        return self._maxSpeed

    @property
    def desiredSpeed(self):
        return self._desiredSpeed