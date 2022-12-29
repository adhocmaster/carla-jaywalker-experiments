from typing import *
import carla
from .ActorClass import ActorClass

class Trajectory:
    def __init__(
        self, 
        actor: carla.Actor,
        actorClass: ActorClass,
        startFrame: int
        ):

        self.actor = actor
        self.actorClass = actorClass
        self.startFrame = startFrame

        self.points:List[Tuple[int, float, float]] = []
    

    def recordPosition(self, currentFrame: int):
        x = self.actor.get_location().x
        y = self.actor.get_location().y
        self.points.append((currentFrame, x, y))
    
    def getPoints(self) -> List[Tuple[int, float, float]]:
        return self.points


