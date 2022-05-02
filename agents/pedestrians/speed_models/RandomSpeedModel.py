from .SpeedModel import SpeedModel
import random

class RandomSpeedModel(SpeedModel):
    
    def initialize(self):
        self._desiredSpeed = self.internalFactors["desired_speed"] * random.uniform(.1,.5)
        self._minSpeed = self.internalFactors["min_crossing_speed"] * random.uniform(1,2)
        self._maxSpeed = self.internalFactors["max_crossing_speed"] * random.uniform(1,2)
        pass