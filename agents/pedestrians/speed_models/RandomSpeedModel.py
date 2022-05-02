from .SpeedModel import SpeedModel
import random

class RandomSpeedModel(SpeedModel):
    
    def initialize(self):
        self._desiredSpeed = self.internalFactors["desired_speed"] * random.randrange(.1,.5, .1)
        self._minSpeed = self.internalFactors["min_crossing_speed"] * random.randrange(1,2,.1)
        self._maxSpeed = self.internalFactors["max_crossing_speed"] * random.randrange(1,2,.1)
        pass