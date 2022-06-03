import carla
import numpy as np
from .CrossingFactorModel import CrossingFactorModel
from ..StateTransitionModel import StateTransitionModel
from ..PedState import PedState
from lib import Utils
from ..PedUtils import PedUtils

class AggressiveCrossingFactorModel(CrossingFactorModel, StateTransitionModel):

    @property
    def name(self):
        return f"AggressiveCrossingFactorModel #{self.agent.id}"
    
    def getOncomingVehicleForce(self):

        if self.actorManager.nearestOncomingVehicle is None:
            return None

        magnitude = self.internalFactors["oncoming_vehicle_speed_force"]
        if magnitude == 0:
            return None
        # extract locations from actors
        ped = self.actorManager.getPedestrians()[0]
        veh = self.actorManager.getVehicles()[0]
        ped_transform = ped.get_transform()
        veh_transform = veh.get_transform()
        ped_loc = ped_transform.location
        veh_loc = veh_transform.location
        # ped_loc = ped_transform.get_location()
        # veh_loc = veh_transform.get_location() 
        # apply algorithm to calculate directional vector
        v_vel = veh.get_velocity()
        d_x = (veh_loc.x + v_vel.x * 0.5 - ped_loc.x) / veh_loc.distance(ped_loc)
        d_y = (veh_loc.y + v_vel.y * 0.5 - ped_loc.y) / veh_loc.distance(ped_loc)
        d_z = (veh_loc.z + v_vel.z * 0.5 - ped_loc.z) / veh_loc.distance(ped_loc)
        d = carla.Vector3D(d_x, d_y, d_z)
        force = d * magnitude
        # nearest_distance = self.actorManager.distanceFromNearestOncomingVehicle()
        # v_vel = veh.get_velocity()
        if v_vel.x < 2 and v_vel.y < 2 and v_vel.z < 2:
            force = self.destDirection * magnitude
            return force
        

        # force = d * magnitude ###
        # force = self.destDirection * magnitude
        return force
            


    def calculateForce(self):
        if self.agent.isCrossing():
            return self.getOncomingVehicleForce()
            
        return None # in other states this model does not produce force
    
    def getNewState(self):

        # return None
        if self.agent.isCrossing() == False:
            return None

        return None

        # self.agent.logger.info(f"Collecting state from {self.name}")

        # # change to survival state if there is a near collision
        # # get the collision point from the head of the vehicle and the center of the pedestrian 

        # # if vehicle is too far, we don't need to even consider it
        # TTC = self.actorManager.pedPredictedTTCNearestOncomingVehicle()
        # if TTC is None:
        #     return None

        
        # conflictPoint = self.agent.getPredictedConflictPoint()
        # if conflictPoint is None:
        #     return None

        # TG = self.agent.getAvailableTimeGapWithClosestVehicle()
        # TTX = PedUtils.timeToCrossNearestLane(self.map, self.agent.location, self.agent._localPlanner.getDestinationModel().getDesiredSpeed())
        
        # diff = TG - TTX # may be too far
        # if diff < self.internalFactors["threshold_ttc_survival_state"] and diff > 0:
        #     return PedState.SURVIVAL

        # if self.internalFactors["threshold_ttc_survival_state"] > TG:
        #     return PedState.SURVIVAL