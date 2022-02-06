import carla
from numpy import empty
from .CrossingFactorModel import CrossingFactorModel
from lib import Utils

class CrossingOncomingFactorModel(CrossingFactorModel):

    @property
    def name(self):
        return f"CrossingOncomingFactorModel #{self.agent.id}"
    
    def getOncomingVehicleForce(self):

        if self.actorManager.nearestOncomingVehicle is None:
            return None

        magnitude = self.internalFactors["oncoming_vehicle_speed_force"]
        if magnitude == 0:
            return None

        return self.destDirection * magnitude

    def calculateForce(self):
        if self.agent.isCrossing():
            return self.getOncomingVehicleForce()
            
        return None # in othe states this model does not produce force