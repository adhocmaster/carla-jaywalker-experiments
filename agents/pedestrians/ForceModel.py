from ast import walk
import carla
from abc import abstractmethod

from lib import ActorManager, ObstacleManager, NotImplementedInterface
from .PedestrianAgent import PedestrianAgent

class ForceModel:

    def __init__(self, agent: PedestrianAgent,  actorManager: ActorManager, obstacleManager: ObstacleManager) -> None:

        self._agent = agent
        self.actorManager = actorManager
        self.obstacleManager = obstacleManager
        pass

    @property
    def agent(self):
        return self._agent

    @abstractmethod
    def calculateForce(self):
        raise NotImplementedInterface("called calculateForce method")

    @abstractmethod
    def getNewState(self):
        raise NotImplementedInterface("getNewState")

        

    
