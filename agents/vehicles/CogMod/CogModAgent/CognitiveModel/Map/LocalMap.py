from turtle import distance
from .GlobalMapManager import GlobalMapManager
from .TrackedAgentManager import TrackedAgentManager


class LocalMap():
    def __init__(self, 
                 vehicle, 
                 destination_transform,
                 vehicle_tracking_radius=100.0, 
                 global_plan_sampling_radius=1.0):
        
        if vehicle is None:
            raise ValueError('need to have vehicle')
            return
        self.vehicle = vehicle
        self.destination_transform = destination_transform
        self.global_plan_sampling_radius = global_plan_sampling_radius # more means less points
        self.vehicle_tracking_radius = vehicle_tracking_radius
        
        self.world = self.vehicle.get_world()
        self.map = self.world.get_map()

        self.global_map_manager = GlobalMapManager(self.map,
                                                    self.vehicle.get_transform(),
                                                    self.destination_transform,
                                                   self.global_plan_sampling_radius)
        self.global_plan = self.global_map_manager.get_global_plan()

        self.trackedAgentManager = TrackedAgentManager(self.vehicle,
                                                       self.vehicle_tracking_radius)

        # tracks agent with interaction type 
        self.tracked_agents = {} # {AGENT: INTERACTION_TYPE}
        # self.tracked_traffic_signs = []

        # self.vehicle_at_front = None

        # print(f'LocalMap is created with map: {self._world}')
        pass

    
    def update(self, global_vehicle_list, del_t):
        # update global plan. discarding the waypoints that are 
        # behind the vehicle's nearest waypoint's 's value' (openDrive)
        self.global_map_manager.update_global_plan(self.vehicle.get_location())

        # update tracked vehicles
        self.trackedAgentManager.update_tracked_agents(global_vehicle_list,
                                                       del_t)
        
        # print the front vehicle speed

        



    def update_traffic_signs(self):
        if len(self.tracked_traffic_signs) == 0:
            all_traffic_signs_from_world = self.world.get_actors().filter("*traffic_light*")
            self.tracked_traffic_signs = all_traffic_signs_from_world
        pass

    def is_done(self):
        return len(self.global_plan) == 0
