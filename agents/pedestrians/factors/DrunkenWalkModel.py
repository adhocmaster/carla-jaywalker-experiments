import carla
from ..ForceModel import ForceModel
from lib import ActorManager, ObstacleManager, NotImplementedInterface
from agents.pedestrians.factors.InternalFactors import InternalFactors
import math
import random
class DrunkenWalkModel(ForceModel):
    def __init__(self, agent: any,  actorManager: ActorManager, obstacleManager: ObstacleManager,
                    internalFactors: InternalFactors) -> None:
        super().__init__(agent, actorManager, obstacleManager, internalFactors)
        self.curr_direction = 1 #1 for right, -1 for left
        self.curr_tick = 0
        self.curr_vector = 0
        self.max_vector = 12
        self.max_period = 25
        self.period_scalar = .1
        
    @property
    def name(self):
        return f"DrunkenWalkModel #{self.agent.id}"

    def reset_period(self):
        self.curr_tick = 0
        self.curr_direction = -1 if self.curr_direction == 1 else 1
        self.max_period = random.randint(15,25)
        self.period_scalar = random.uniform(.05, .5)
        self.max_vector = random.randint(5, 15)

    def calculateForce(self):
        print("CALCULATING FORCE OF STUFFn\n\n\n\n\n\n", self.curr_tick)
        if self.curr_tick >= self.max_period:
            self.reset_period()
        self.curr_vector = self.max_vector*math.cos(self.period_scalar*self.curr_tick)
        self.curr_tick+= 1
        return carla.Vector3D(x=self.curr_vector, y=1, z=1)