
from ..ForceModel import ForceModel

class CrossingFactorModel(ForceModel):

    def setDestinationParams(self, force, direction, speed):
        self.destForce = force
        self.destDirection = direction
        self.destSpeed = speed

