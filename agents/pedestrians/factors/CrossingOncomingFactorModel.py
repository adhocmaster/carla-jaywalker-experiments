import carla
import numpy as np
from .CrossingFactorModel import CrossingFactorModel
from ..StateTransitionModel import StateTransitionModel
from ..PedState import PedState
from lib import Utils, VehicleUtils, ForceFunctions
from ..PedUtils import PedUtils

class CrossingOncomingFactorModel(CrossingFactorModel, StateTransitionModel):
    """We implement the model from 
    Yang, Dongfang et al. “A Social Force Based Pedestrian Motion Model Considering Multi-Pedestrian Interaction with a Vehicle.” ACM Transactions on Spatial Algorithms and Systems (TSAS) 6 (2020): 1 - 27.

    """

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
        # if self.flinchRequired():
        #     self.agent.logger.info("Flinching back")
        #     force = carla.Vector3D() - force * 100

        return force

    
    def getYANGForce(self) -> carla.Vector3D:
        if self.actorManager.nearestOncomingVehicle is None:
            return None

        A_veh = 777.5852
        b_veh = 2.613755
        lambda_veh = 0.3119132

        p_v = VehicleUtils.getNearestPointOnYANGVehicleContour(self.actorManager.nearestOncomingVehicle, self.agent.location) #influential point on the vehicle contour

        distanceToVeh = self.agent.location.distance_2d(p_v)

        n_vit = (self.agent.location - p_v).make_unit_vector() # direction from the influential point to the ped.


        radAngle = Utils.angleBetweenDirections(-1 * n_vit, self.agent.direction)
        # print("distanceToVeh", distanceToVeh)
        # print("n_vit", n_vit)
        # print("radAngle", radAngle)

        force = ForceFunctions.expForce(distanceToVeh, A_veh, b_veh) * ForceFunctions.anisotropySin(radAngle, lambda_veh) * n_vit
        # print("force", force)


        return force


    # def flinchRequired(self):

    #     conflictPoint = self.agent.getPredictedConflictPoint()
    #     if conflictPoint is None:
    #         return False

    #     TG = self.agent.getAvailableTimeGapWithClosestVehicle()
    #     TTX = PedUtils.timeToCrossNearestLane(self.map, self.agent.location, self.agent._localPlanner.getDestinationModel().getDesiredSpeed())
        
    #     diff = TG - TTX # may be too far
    #     if diff < 1 and diff > 0:
    #         return True
    #     return False
            


    def calculateForce(self) -> carla.Vector3D:
        if self.agent.isCrossing():
            return self.getYANGForce()
            # return self.getOncomingVehicleForce()
            
        return None # in othe states this model does not produce force


        
    def getNewState(self):

        # return None
        if self.agent.isCrossing() == False:
            return None

        return None

        # self.agent.logger.info(f"Collecting state from {self.name}")

        # # change to survival state if there is a near collision
        # # get the collision point from the head of the vehicle and the center of the pedestrian 

        # # if vehicle is too far, we don't need to even consider it
        # # TTC = self.actorManager.pedPredictedTTCNearestOncomingVehicle()
        # # if TTC is None:
        # #     return None

        
        # conflictPoint = self.agent.getPredictedConflictPoint()
        # if conflictPoint is None:
        #     return None

        # TG = self.agent.getAvailableTimeGapWithClosestVehicle()
        # TTX = PedUtils.timeToCrossNearestLane(self.map, self.agent.location, self.agent._localPlanner.getDestinationModel().getDesiredSpeed())
        
        # diff = TG - TTX # may be too far
        # if diff < self.internalFactors["threshold_ttc_survival_state"] and diff > 0:
        #     return PedState.SURVIVAL

        # # if self.internalFactors["threshold_ttc_survival_state"] > TG:
        # #     return PedState.SURVIVAL