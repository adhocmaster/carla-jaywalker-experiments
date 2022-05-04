from .SpeedModel import SpeedModel
import random

class RandomSpeedModel(SpeedModel):
    
    def initialize(self):
        self._desiredSpeed = self.internalFactors["desired_speed"] * random.uniform(2,10)
        self._minSpeed = self.internalFactors["min_crossing_speed"] * random.uniform(1,4)
        self._maxSpeed = self.internalFactors["max_crossing_speed"] * random.uniform(1,4)
        pass