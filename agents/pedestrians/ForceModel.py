from ast import walk
import carla
from abc import abstractmethod

from lib import ActorManager, ObstacleManager
from .PedestrianAgent import PedestrianAgent

class ForceModel:

    def __init__(self, agent: PedestrianAgent,  actorManager: ActorManager, obstacleManager: ObstacleManager) -> None:

        self._agent = agent
        self.actorManager = actorManager
        self.obstacleManager = obstacleManager
        pass

    @property
    def agent(self):
        return self.agent

    @abstractmethod
    def calculateForce(self):
        raise Exception("called abstract method")
    
