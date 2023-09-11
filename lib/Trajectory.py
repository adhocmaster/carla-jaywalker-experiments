from typing import *
import carla
from .ActorClass import ActorClass
from time import time

X = Tuple[float, float]
Y = float
Heading = float
Frame = int
Record = Tuple[Frame, X, Y, Heading]


class Trajectory:
    def __init__(
        self, 
        actor: carla.Actor,
        actorClass: ActorClass,
        startFrame: int,
        meta: Dict[str, any]
        ):

        self.actor = actor
        self.actorClass = actorClass
        self.startFrame = startFrame
        self.meta = meta

        self.points:List[Record] = []
    

    def recordPosition(self, currentFrame: int):
        if self.actor.is_alive == False:
            return
        x = self.actor.get_location().x
        y = self.actor.get_location().y
        heading = self.actor.get_transform().rotation.yaw
        self.points.append((currentFrame, x, y, heading))
    
    def getPoints(self) -> List[Record]:
        return self.points


