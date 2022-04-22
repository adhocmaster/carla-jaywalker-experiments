from .SpeedModel import SpeedModel

class StaticSpeedModel(SpeedModel):
    
    def initialize(self):
        self._desiredSpeed = self.internalFactors["desired_speed"] * 0.5
        self._minSpeed = self.internalFactors["min_crossing_speed"] * 2
        self._maxSpeed = self.internalFactors["max_crossing_speed"] * 2
        pass