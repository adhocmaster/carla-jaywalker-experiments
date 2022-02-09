import carla
import numpy as np
from .CrossingFactorModel import CrossingFactorModel
from ..StateTransitionModel import StateTransitionModel
from ..PedState import PedState
from lib import Utils
from ..PedUtils import PedUtils

class CrossingOncomingFactorModel(CrossingFactorModel, StateTransitionModel):

    @property
    def name(self):
        return f"CrossingOncomingFactorModel #{self.agent.id}"
    
    def getOncomingVehicleForce(self):

        if self.actorManager.nearestOncomingVehicle is None:
            return None

        magnitude = self.internalFactors["oncoming_vehicle_speed_force"]
        if magnitude == 0:
            return None

        force = self.destDirection * magnitude
        # Do we need to flinch back? If so, increase the force and multiply it with 10.
        if self.flinchRequired():
            self.agent.logger.info("Flinching back")
            force = carla.Vector3D() - force

        return force

    def flinchRequired(self):

        TG = self.agent.getAvailableTimeGapWithClosestVehicle()
        TTX = PedUtils.timeToCrossNearestLane(self.map, self.agent.location, self.agent._localPlanner.getDestinationModel().getDesiredSpeed())
        
        # return np.random.choice([True, False], p=[0.5, 0.5])


    def calculateForce(self):
        if self.agent.isCrossing():
            return self.getOncomingVehicleForce()
            
        return None # in othe states this model does not produce force


        
    def getNewState(self):
        if self.agent.isCrossing() == False:
            return None

        # change to survival state if there is a near collision
        # get the collision point from the head of the vehicle and the center of the pedestrian 

        # if vehicle is too far, we don't need to even consider it
        TTC = self.actorManager.pedTTCNearestOncomingVehicle()
        if TTC is None:
            return None

        if self.internalFactors["threshold_ttc_survival_state"] > TTC:
            return PedState.SURVIVAL