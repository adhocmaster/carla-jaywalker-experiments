from .SpeedModel import SpeedModel
import math

class RelaxationSpeedModel(SpeedModel):

    """
    Can we build this using any real world data.
    """
    
    def initialize(self):
        self._desiredSpeed = self.getBaseSpeed()
        self._minSpeed = self.getBaseSpeed()
        self._maxSpeed = self.getBaseSpeed()
        pass


    def getBaseSpeed(self):
        c = self.internalFactors["relaxation_speed_model_coeff"] # lower the c, higher the steepnes
        r = self.internalFactors["relaxation_time"] 
        maxSpeed = self.internalFactors["max_crossing_speed"]
        relaxationTimeCoefficient = r
        if r < 0.1:
            relaxationTimeCoefficient = 0.1
        if r > 2:
            relaxationTimeCoefficient = 2

        # speed =  (self.internalFactors["max_crossing_speed"]) / (1 + math.exp(c * self.internalFactors["relaxation_time"]))
        speed =  (maxSpeed) / (maxSpeed * relaxationTimeCoefficient)

        self.agent.logger.info(f"c={c} max_crossing_speed={self.internalFactors['max_crossing_speed']} relaxation_time={self.internalFactors['relaxation_time']} speed={speed}")
        # self.agent.logger.info(f"denominator={1 + math.exp(c * self.internalFactors['relaxation_time'])}")
        return speed

