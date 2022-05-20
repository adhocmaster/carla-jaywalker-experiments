from lib import NotImplementedInterface
from abc import abstractmethod, abstractclassmethod
from research import BaseResearch
from lib import EpisodeSimulator, LoggerFactory, SimulationMode
import carla

import gym
from typing import Generic, Optional, SupportsFloat, Tuple, TypeVar, Union
ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")

class Environment(gym.Env):

    """
    Environment has no relation with the RL agent. It's sole job is to provide 3 methods: reset, close, and step. It contains the research object
    """
    def __init__(self, 
                 research: BaseResearch
                 ) -> None:
                 
        super().__init__()
        self.logger = research.logger
        self.research = research
        self.tickCounter = None
        self.setObsActionSpaces()
        self.reset()
        pass

    @abstractclassmethod
    def create():
        raise NotImplementedInterface("create")



    def reset(
        self,
        *,
        seed: Optional[int] = None,
        return_info: bool = False,
        options: Optional[dict] = None,
    ) -> Union[ObsType, Tuple[ObsType, dict]]:

        self.tickCounter = 0
        self.research.reset()
        # raise NotImplementedInterface("reset")
        if not return_info:
            return self.state()
        else:
            return self.state(), {}

    def close(self):
        self.research.reset()

    def render(self, mode="human"):
        raise NotImplementedError("render")

    def step(self, action: ActType) -> Tuple[ObsType, float, bool, dict]:
        """
            executes the step (changes the behavior parameters). ticks, and returns the new state. 
            However an action may need multiple ticks to be completed. So, this method must not return a new state every tick.
            returns new_state, reward, done, _
        """
        # self.tickCounter += 1
        self.updateBehavior(action)
        self.tickUntilActionIsFinished(action)
        newState = self.state()
        done = self.isEpisodeDone()
        reward = self.reward()
        return newState, reward, done, None
        # raise NotImplementedInterface("action")

    
    def tickUntilActionIsFinished(self, action: ActType):
        n = self.getActionTicks(action)
        self.logger.info(f"tickUntilActionIsFinished n={n}")
        for _ in range(n):
            self.tickCounter += 1
            self.research.simulator.tick(self.tickCounter) #episodic

    def isEpisodeDone(self):
        return self.research.simulator.isDone()

    @abstractmethod
    def setObsActionSpaces(self):
        raise NotImplementedInterface("setObsActionSpaces")

    @abstractmethod
    def reward(self):
        raise NotImplementedInterface("reward")

    @abstractmethod
    def state(self):
        raise NotImplementedInterface("state")

    
    @abstractmethod
    def getActionTicks(self, action) -> int:
        """actionTime/time_delta"""
        raise NotImplementedInterface("getActionTicks")


    @abstractmethod
    def updateBehavior(self, action: ActType):
        # self.logger.info("Updating behavior")
        raise NotImplementedInterface("updateBehavior")


