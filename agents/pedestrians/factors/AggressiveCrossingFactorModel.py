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
        d_x = (veh_loc.x - ped_loc.x) / veh_loc.distance(ped_loc)
        d_y = (veh_loc.y - ped_loc.y) / veh_loc.distance(ped_loc)
        d_z = (veh_loc.z - ped_loc.z) / veh_loc.distance(ped_loc)
        d =carla.Vector3D(d_x, d_y, d_z)
        # move toward original destination after passing conflict point
        # nearest_distance = self.actorManager.distanceFromNearestOncomingVehicle()
        # if nearest_distance < 5:
        #     force = self.destDirection * magnitude
        # else:
        #     force = d * magnitude
        

        # force = d * magnitude ###
        # force = self.destDirection * magnitude
        return force
            


    def calculateForce(self):
        if self.agent.isCrossing():
            return self.getOncomingVehicleForce()
            
        return None # in other states this model does not produce force
    
    def getNewState(self):
        return None