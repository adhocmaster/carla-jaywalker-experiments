from .SpeedModel import SpeedModel
import random

class RandomSpeedModel(SpeedModel):
    
    def initialize(self):
        self._desiredSpeed = self.internalFactors["desired_speed"] * random.uniform(4,10)
        self._minSpeed = self.internalFactors["min_crossing_speed"] * random.uniform(1,self.internalFactors["desired_speed"] - 1)
        self._maxSpeed = self.internalFactors["max_crossing_speed"] * random.uniform(self.internalFactors["desired_speed"] + 5,20)
        pass