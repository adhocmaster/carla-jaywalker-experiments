
from time import time
from typing import *
from collections import defaultdict
import pandas as pd
import carla

from agents.pedestrians.PedestrianAgent import PedestrianAgent
from agents.vehicles.SpeedControlledBehaviorAgent import SpeedControlledBehaviorAgent
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
        self.vehicles: Dict[int, SpeedControlledBehaviorAgent] = {}
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

    def addVehicle(self, vehicleAgent: SpeedControlledBehaviorAgent, currentFrame: int, meta: Dict[str, any]):
        self.addActor(
                actor=vehicleAgent.vehicle, 
                actorClass=ActorClass.vehicle, 
                currentFrame=currentFrame, 
                meta=meta
            )
        self.vehicles[vehicleAgent.vehicle.id] = vehicleAgent

    
    def collectStats(self, frameNo: int) -> None:
        # trajectory element = (mapX, mapY, agentSpeed, )
        # for actor in self.actors:
        for actorId, traj in self.trajectories.items():
            state = "NA"
            if actorId in self.pedestrians:
                state = self.pedestrians[actorId].state.value
            traj.recordPosition(frameNo, state)
    
    def getAsDataFrame(self) -> pd.DataFrame:

        dfs = []
        for actor in self.actors:
            trajectory = self.trajectories[actor.id]
            points = trajectory.getPoints()
            trackDf = pd.DataFrame(points, columns= ["frame", "x", "y", "heading", "state"])
            trackDf["recordingId"] = self.episodeNo
            trackDf["trackId"] = actor.id
            trackDf["class"] = trajectory.actorClass.value
            dfs.append(trackDf[['recordingId', 'trackId', 'class', 'frame', 'x', 'y', "heading", "state"]])
        
        return pd.concat(dfs, ignore_index=True)
    
    def getMeta(self) -> Dict[str, any]:

        combined = {
            "recordingId": self.episodeNo,
            "timestamp": time(),
            "fps": self.fps,
            "participants": [
                self.getParticipantMeta(p) for p in self.trajectories.values()
            ]
        }

        # print(combined)

            

        combined.update(self.meta)
        return combined
    
    def getParticipantMeta(self, trajectory: Trajectory) -> Dict[str, any]:
        meta = {
            "id": trajectory.actor.id,
            "class": trajectory.actorClass.value,
            "meta": trajectory.meta
        }
        if trajectory.actorClass == ActorClass.vehicle:
            meta["maxSpeed"] = self.vehicles[trajectory.actor.id].maxSpeed
        return meta
    



