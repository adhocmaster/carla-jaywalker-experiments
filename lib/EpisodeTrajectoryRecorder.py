
from typing import *
from collections import defaultdict
import pandas as pd
import carla
from .ActorClass import ActorClass
from .Trajectory import Trajectory

class EpisodeTrajectoryRecorder:
    """Per episode"""

    def __init__(
        self, 
        episodeNo: int,
        roadConfiguration: Dict[str, any], 
        fps: float,
        startFrame: int = 0
        ):

        self.episodeNo = episodeNo
        self.roadConfiguration = roadConfiguration
        self.fps = fps
        self.startFrame = startFrame

        self.actors = set([])
        self.trajectories = {}

    
    def addactor(
        
        self, 
        actor: carla.Actor, 
        actorClass: ActorClass,
        currentFrame: int
        ):
        """Actors can be added any time.

        Args:
            actor (carla.Actor): _description_
            actorClass (ActorClass): _description_
        """
        if actor in self.actors:
            return
            
        self.actors.add(actor)

        self.trajectories[actor.id] = Trajectory(
            actor=actor,
            actorClass=actorClass,
            startFrame=currentFrame
        )


    
    def collectStats(self, currentFrame: int):
        # trajectory element = (mapX, mapY, agentSpeed, )
        # for actor in self.actors:
        for traj in self.trajectories.values():
            traj.recordPosition(currentFrame)
    
    def getAsDataFrame(self) -> pd.DataFrame:

        dfs = []
        for actorId, traj in self.trajectories.items():
            points = traj.getPoints()
            trackDf = pd.DataFrame(points, columns= ["frame", "mapX", "mapY"])
            trackDf["episode"] = self.episodeNo
            dfs.append(trackDf)
        
        return pd.concat(dfs, ignore_index=True)
    
    



