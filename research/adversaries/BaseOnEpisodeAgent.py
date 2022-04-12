from lib import NotImplementedInterface

class BaseOnEpisodeAgent:
    """
    This agent can change pedestrian state during an episode.
    time delta needs to be a parameter for time delta invariancy
    We need a state
    we need a step function
    """

    def onTick(self, world_snapshot):
        raise NotImplementedInterface("onTick")

    
