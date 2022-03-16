from ...lib import NotImplementedInterface
from abc import abstractmethod
from ...research import BaseResearch

class Environment:

    """
    Environment has no relation with the RL agent. It's sole job is to provide 3 methods: reset, close, and step. It contains the research object
    """

    def __init__(self, research: BaseResearch) -> None:
        self.research = research
        pass

    @abstractmethod
    def reset(self):
        raise NotImplementedInterface("reset")

    @abstractmethod
    def close(self):
        raise NotImplementedInterface("close")

    @abstractmethod
    def step(self, action):
        """
            executes the step (changes the behavior parameters). ticks, and returns the new state
            returns new_state, reward, done, _
        """
        self.updateBehavior(action)
        self.tick()
        newState = self.state()
        done = self.done()
        reward = self.reward()
        return newState, reward, done, None
        # raise NotImplementedInterface("action")

    @abstractmethod
    def updateBehavior(self):
        raise NotImplementedInterface("updateBehavior")

    @abstractmethod
    def reward(self):
        raise NotImplementedInterface("reward")

    @abstractmethod
    def done(self):
        raise NotImplementedInterface("done")

    @abstractmethod
    def state(self):
        raise NotImplementedInterface("state")

