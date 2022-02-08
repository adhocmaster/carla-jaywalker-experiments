
from ..ForceModel import ForceModel

class CrossingFactorModel(ForceModel):

    def setDestinationParams(self, force, direction, speed):
        """We need some parameters from destination model

        Args:
            force ([type]): [description]
            direction ([type]): [description]
            speed ([type]): [description]
        """
        self.destForce = force
        self.destDirection = direction
        self.destSpeed = speed

