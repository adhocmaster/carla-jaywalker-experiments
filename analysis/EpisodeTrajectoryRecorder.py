
from time import time
from typing import *
from collections import defaultdict
import pandas as pd
import carla

from agents.pedestrians.PedestrianAgent import PedestrianAgent
from lib.ActorClass import ActorClass
from lib.Trajectory import Trajectory

class EpisodeTrajectoryRecorder:
    """Per episode"""

    def __init__(
        self, 
        episodeNo: int,
        initialWorldSnapshot: carla.WorldSnapshot,
        meta: Dict[str, any], 
        fps: float,
        startFrame: int = 0,
        ):

        self.episodeNo = episodeNo
        self.initialWorldSnapshot = initialWorldSnapshot
        self.meta = meta
        self.fps = fps
        self.startFrame = startFrame

        self.actors = set([])
        self.pedestrians: Dict[int, PedestrianAgent] = {}
        self.trajectories: Dict[int, Trajectory] = {}

    
    def addActor(
        
        self, 
        actor: carla.Actor, 
        actorClass: ActorClass,
        currentFrame: int,
        meta: Dict[str, any]
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
            startFrame=currentFrame,
            meta=meta
        )

    def addPedestrian(self, pedestrian: PedestrianAgent, currentFrame: int, meta: Dict[str, any]):
        self.addActor(
                actor=pedestrian.walker, 
                actorClass=ActorClass.pedestrian, 
                currentFrame=currentFrame, 
                meta=meta
            )
        self.pedestrians[pedestrian.walker.id] = pedestrian

    
    def collectStats(self, frameNo: int) -> None:
        # trajectory element = (mapX, mapY, agentSpeed, )
        # for actor in self.actors:
        for traj in self.trajectories.values():
            traj.recordPosition(frameNo)
    
    def getAsDataFrame(self) -> pd.DataFrame:

        dfs = []
        for actor in self.actors:
            trajectory = self.trajectories[actor.id]
            points = trajectory.getPoints()
            trackDf = pd.DataFrame(points, columns= ["frame", "x", "y", "heading"])
            trackDf["recordingId"] = self.episodeNo
            trackDf["trackId"] = actor.id
            trackDf["class"] = trajectory.actorClass.value
            dfs.append(trackDf[['recordingId', 'trackId', 'class', 'frame', 'x', 'y', "heading"]])
        
        return pd.concat(dfs, ignore_index=True)
    
    def getMeta(self) -> Dict[str, any]:

        combined = {
            "recordingId": self.episodeNo,
            "timestamp": time(),
            "fps": self.fps,
            "participants": [
                {"id": p.actor.id, "class": p.actorClass.value, "meta": p.meta} for p in self.trajectories.values()
            ]
        }

        # print(combined)

            

        combined.update(self.meta)
        return combined
    
    



