from ...lib import NotImplementedInterface
from abc import abstractmethod, abstractclassmethod
from ...research import BaseResearch
from ...lib import EpisodeSimulator, LoggerFactory
import carla
from SimulationMode import SimulationMode

class Environment:

    """
    Environment has no relation with the RL agent. It's sole job is to provide 3 methods: reset, close, and step. It contains the research object
    """
    def __init__(self, 
                 research: BaseResearch
                 ) -> None:
                 
        self.logger = research.logger
        self.research = research
        self.tickCounter = None
        self.reset()
        pass

    @abstractclassmethod
    def create():
        raise NotImplementedInterface("create")

    # @abstractmethod
    def reset(self):
        self.tickCounter = 0
        self.research.reset()
        # raise NotImplementedInterface("reset")

    # @abstractmethod
    def close(self):
        self.research.reset()
        # raise NotImplementedInterface("close")

    # @abstractmethod
    def step(self, action):
        """
            executes the step (changes the behavior parameters). ticks, and returns the new state
            returns new_state, reward, done, _
        """
        self.tickCounter += 1
        self.updateBehavior(action)
        self.research.simulator.tick(self.tickCounter) #episodic
        newState = self.state()
        done = self.isEpisodeDone()
        reward = self.reward()
        return newState, reward, done, None
        # raise NotImplementedInterface("action")

    def isEpisodeDone(self):
        return self.research.simulator.isDone()

    @abstractmethod
    def updateBehavior(self):
        # self.logger.info("Updating behavior")
        raise NotImplementedInterface("updateBehavior")

    @abstractmethod
    def reward(self):
        raise NotImplementedInterface("reward")

    @abstractmethod
    def state(self):
        raise NotImplementedInterface("state")

