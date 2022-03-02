from enum import Enum
from turtle import distance
from agents.navigation.global_route_planner import GlobalRoutePlanner
from .GeometryHelper import GeometryHelper

class InteractionType(Enum):
    FOLLOW = 1
    CROSS = 2
    MERGE = 3
    NONCONFLICT = 4


class LocalMap():
    def __init__(self, vehicle, destination_transform,
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

        
        self.global_planner = GlobalRoutePlanner(self.map, 
                                                 self.global_plan_sampling_radius)
        self.global_plan = self.set_global_plan(self.destination_transform)
        # self.cur_road_id = self.global_plan[0][0].road_id


        self.road_list = self.create_road_list_from_global_plan()
        
        self.tracked_agents = {} # {AGENT: INTERACTION_TYPE}
        self.tracked_traffic_signs = []

        self.vehicle_at_front = None

        # print(f'LocalMap is created with map: {self._world}')
        pass

    def create_road_list_from_global_plan(self):
        road_dict = {}
        road_list = []
        for wp, _ in self.global_plan:
            # print(f'road id: {wp.road_id}, s: {wp.s}')
            if wp.road_id not in road_dict.keys():
                road_dict[wp.road_id] = True
                road_list.append(wp.road_id)
                pass
            
        
        print(f'road dict {road_dict}')
        return road_list


    def set_global_plan(self, end_transform):

        start_transform = self.vehicle.get_transform()
        if not start_transform or not end_transform:
            raise ValueError('need to have start and end for global plan')
        print(f'start transform: {start_transform}, \nend transform: {end_transform}')
        return self.global_planner.trace_route(start_transform.location, end_transform.location)
        pass

    def get_global_plan(self):
        if self.global_plan is None:
            raise ValueError('need to have global plan')
            return None
        return self.global_plan

    # 
    def update(self, global_agent_list):
        
        # update global plan. discarding the waypoints that are 
        # behind the vehicle's nearest waypoint's 's value' (openDrive)
        self.update_global_plan()

        # update tracked vehicles
        self.update_tracked_agents(global_agent_list)

        # # update tracked traffic signs
        # self.update_traffic_signs()

        # current_map_dict = {'route': self.global_plan,
        #                     'tracked_vehicles': self.tracked_vehicles,
        #                     'tracked_traffic_signs': self.tracked_traffic_signs}

        # return current_map_dict



    def update_traffic_signs(self):
        if len(self.tracked_traffic_signs) == 0:
            all_traffic_signs_from_world = self.world.get_actors().filter("*traffic_light*")
            self.tracked_traffic_signs = all_traffic_signs_from_world



    def update_tracked_agents(self, global_agent_list):

        # print(f'global agent list length: {len(global_agent_list)}')
        # remove agent that are out of the tracking radius
        self.remove_agent_beyond_tracking_radius()

        # # add new agent that are in the tracking radius
        self.append_new_agents_inside_tracking_radius(global_agent_list)

        # print(f'tracked agents: {self.tracked_agents}')
        follow_agent = []
        merge_agent = []
        cross_agent = []

        for agent, interaction_type in self.tracked_agents.items():
            if interaction_type == InteractionType.FOLLOW:
                follow_agent.append(agent)
            elif interaction_type == InteractionType.MERGE:
                merge_agent.append(agent)
            elif interaction_type == InteractionType.CROSS:
                cross_agent.append(agent)
            pass

        min_distance = 9999
        for agent in follow_agent:
            distance = self.vehicle.get_location().distance(agent.vehicle.get_location())
            if distance < min_distance:
                min_distance = distance
                self.vehicle_at_front = agent.vehicle
                # print('setting vehuicle at front ')
                pass




        # for agent in self.tracked_agents.values():
        #     agent_global_plan = agent.local_map.get_global_plan()
        #     intersection = GeometryHelper.is_intersecting(self.global_plan, agent_global_plan)
        #     # print(f'intersection: {len(intersection)}')
        #     pass
        

        # vehicle_at_front = None
        # for v_id, vehicle in self.tracked_vehicles.items():
        #     vehicle_global_plan = vehicle.local_map.get_global_plan()
        #     print(f'global plan: {vehicle_global_plan}')
        #     pass


    def set_interaction_type(self, agent):
        agent_global_plan = agent.local_map.get_global_plan()
        intersection = GeometryHelper.is_intersecting(self.global_plan, agent_global_plan)
        if intersection.type == 'LineString':
            return InteractionType.NONCONFLICT
        if intersection.type == 'Point':
            return InteractionType.CROSS
        if intersection.type == 'MultiLineString':
            if agent.local_map.road_list[0] == self.road_list[0]:
                return InteractionType.FOLLOW
            else:
                return InteractionType.MERGE
        print(f'intersection {intersection.type}')
        
        
        pass




    def append_new_agents_inside_tracking_radius(self, global_agent_list):
        # all_vehicle_from_world = self.world.get_actors().filter('vehicle.*')
        other_agent_from_world = global_agent_list
        # self.tracked_vehicles = []
        for agent in other_agent_from_world:
            distance = self.vehicle.get_location().distance(agent.vehicle.get_location())
            if distance > self.vehicle_tracking_radius:
                continue
            else:
                if agent not in self.tracked_agents.keys():
                    self.tracked_agents[agent] = self.set_interaction_type(agent)
                    pass
                pass
        pass

    def remove_agent_beyond_tracking_radius(self):
        copy_tracked_vehicles = self.tracked_agents.copy()
        
        for agent, interaction_type in copy_tracked_vehicles.items():
            distance = self.vehicle.get_location().distance(agent.vehicle.get_location())
            if distance > self.vehicle_tracking_radius:
                del self.tracked_agents[agent]
                pass



        


    def update_global_plan(self):

        tuple_to_discard = []
        nearest_waypoint = self.map.get_waypoint(self.vehicle.get_location())
        
        # sometimes due to high speed vehcile misses some waypoint at the end of the roads
        #  next block ensures all the waypoints are removed properly
        # print(f'nearest road id: {nearest_waypoint.road_id}, self.road list {self.road_list}')
        
        self.remove_residual_waypoints(tuple_to_discard, nearest_waypoint)

        self.remove_waypoint_on_same_road(tuple_to_discard, nearest_waypoint)

        # print(f'tuple to discard: {len(tuple_to_discard)}')

        self.discard_tuple_from_global_plan(tuple_to_discard)



    def discard_tuple_from_global_plan(self, tuple_to_discard):
        if len(tuple_to_discard) != 0:
            for ttd in tuple_to_discard:
                self.global_plan.remove(ttd)
                pass

    def remove_waypoint_on_same_road(self, tuple_to_discard, nearest_waypoint):
        for wp, ro in self.global_plan:
            # print(f'wp road id : {wp.road_id}, s {wp.s}, nearest {nearest_waypoint.road_id}, s {nearest_waypoint.s}')
            if wp.road_id == nearest_waypoint.road_id:
                # need this for the road direction formation according to 
                # OpenDRIVE's road direction
                if wp.lane_id < 0:
                    if wp.s <= nearest_waypoint.s:
                        tuple_to_discard.append((wp, ro))
                elif wp.lane_id > 0:
                    if wp.s >= nearest_waypoint.s:
                        tuple_to_discard.append((wp, ro))

    def remove_residual_waypoints(self, tuple_to_discard, nearest_waypoint):
        for i in self.road_list:
            if nearest_waypoint.road_id == i:
                while nearest_waypoint.road_id != self.road_list[0]:
                    for wp, ro in self.global_plan:
                        if wp.road_id == self.road_list[0]:
                            tuple_to_discard.append((wp, ro))
                    
                    # self.cur_road_id = nearest_waypoint.road_id
                    self.road_list.pop(0)
                break
                
    
    def is_done(self):
        return len(self.global_plan) == 0









    # def update_global_plan(self):
    #     tuple_to_discard = []
    #     for wp, ro in self.global_plan:
    #         distance = self.vehicle.get_location().distance(wp.transform.location)
    #         # print(f'vehicle location: {self._vehicle.get_location()}')
    #         # print(f'wp: {wp.transform.location}, distance: {distance}')
    #         if distance < self._waypoint_tracking_radius:
    #             tuple_to_discard.append((wp, ro))
    #             pass
    #     if len(tuple_to_discard) != 0:
    #         for ttd in tuple_to_discard:
    #             # print(f'discarding waypoint: {ttd[0]}')
    #             self.global_plan.remove(ttd)
    #             pass
