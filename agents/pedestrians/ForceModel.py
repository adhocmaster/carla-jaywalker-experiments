from ast import walk
import carla
from abc import abstractmethod

from lib import ActorManager, ObstacleManager, NotImplementedInterface
# from agents.pedestrians.PedestrianAgent import Pedestria.Agent
from agents.pedestrians.factors.InternalFactors import InternalFactors

class ForceModel:

    def __init__(self, agent: any,  actorManager: ActorManager, obstacleManager: ObstacleManager,
                    internalFactors: InternalFactors) -> None:

        self._agent = agent
        self.actorManager = actorManager
        self.obstacleManager = obstacleManager
        self.internalFactors = internalFactors
        pass

    @property
    def agent(self):
        return self._agent

    @property
    def map(self):
        return self.world.get_map()

    @property
    def world(self):
        return self.agent._world

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedInterface("name")
        

    @abstractmethod
    def calculateForce(self):
        raise NotImplementedInterface("called calculateForce method")

    @abstractmethod
    def getNewState(self):
        raise NotImplementedInterface("getNewState")

    # @abstractmethod
    # def isEphemeral(self, ticks):
    #     raise NotImplementedInterface("isEphemeral")

    # @abstractmethod
    # def activate(self, ticks):
    #     raise NotImplementedInterface("activate")

    # @abstractmethod
    # def deactivate(self, ticks):
    #     raise NotImplementedInterface("deactivate")


        

    
