

from .WorkingMemory import WorkingMemory
from .GeometryHelper import GeometryHelper
from enum import Enum


class InteractionType(Enum):
    FOLLOW = 1
    CROSS = 2
    MERGE = 3
    NONCONFLICT = 4

class TrackedAgentManager:

    def __init__(self, vehicle, vehicle_tracking_radius=100):

        self.vehicle = vehicle
        self.world = vehicle.get_world()
        self.vehicle_tracking_radius = vehicle_tracking_radius
        self.tracked_agents = {}

        # final version will have 8 zones
        # todo: add other zones
        self.surrounding_agents = {
            'front': WorkingMemory(),
        }

        self.previous_vehicle_location = self.vehicle.get_location()
        self.previous_vehicle_velocity = self.vehicle.get_velocity()

        pass

    def is_there_vehicle(self, direction):
        if direction not in self.surrounding_agents:
            raise ValueError('only front is supported')
        return self.surrounding_agents[direction].is_set()

    def update_tracked_agents(self, global_vehicle_list, del_t):
        
        cur_ego_velocity = self.vehicle.get_velocity()
        cur_ego_location = self.vehicle.get_location()

        # remove agent that are out of the tracking radius
        # self.remove_agent_beyond_tracking_radius()

        # # add new agent that are in the tracking radius
        self.append_new_agents_inside_tracking_radius(global_vehicle_list, del_t)

        follow_agent = []
        merge_agent = []
        cross_agent = []

        exact_update_agent_list = [vehicle.id for vehicle in global_vehicle_list]
        approximate_update_agent_list = list(set(self.tracked_agents.keys()) - set(exact_update_agent_list))
        # print('all veh: ', len(global_vehicle_list), ' tracked_agent ', self.tracked_agents.keys(), ' exact: ', exact_update_agent_list, ' approx: ', approximate_update_agent_list)

        agent_to_zone_map = {}
        for key, val in self.surrounding_agents.items():
            if val.is_set():
                agent_to_zone_map[val.get_agent_id()] = key
        
        # print('agent to zone map: ', agent_to_zone_map)

        for agent in exact_update_agent_list:
            # print(agent, exact_update_agent_list)
            if agent in agent_to_zone_map.keys():
                print('inside if exact ')
                other_vehicle = self.world.get_actor(agent)
                zone = agent_to_zone_map[agent]
                self.surrounding_agents[zone].update(ego_vehicle=self.vehicle, 
                                                     other_vehicle=other_vehicle,
                                                     del_t=del_t)
        for agent in approximate_update_agent_list:
            # print(agent, approximate_update_agent_list)
            if agent in agent_to_zone_map.keys():
                print('inside if approximate ')
                zone = agent_to_zone_map[agent]
                self.surrounding_agents[zone].update(ego_vehicle=self.vehicle, 
                                                     other_vehicle=None,
                                                     del_t=del_t)
            
              
        
        self.previous_vehicle_location = cur_ego_location
        self.previous_vehicle_velocity = cur_ego_velocity

    def append_new_agents_inside_tracking_radius(self, global_vehicle_list, del_t):
        other_vehicle_from_world = global_vehicle_list
        for vehicle in other_vehicle_from_world:
            if vehicle is None:
                continue
            distance = self.vehicle.get_location().distance(vehicle.get_location())
            print(f'distance {distance}, tracking radius {self.vehicle_tracking_radius}')
            if distance > self.vehicle_tracking_radius:
                continue
            else:
                if vehicle.id not in self.tracked_agents.keys():
                    self.tracked_agents[vehicle.id] = InteractionType.FOLLOW
                    self.surrounding_agents['front'].set_agent(vehicle, self.vehicle)                                                             
                    pass
                pass
        # print(f'tracked agents: {self.tracked_agents}')
        pass

    def remove_agent_beyond_tracking_radius(self):
        copy_tracked_vehicles = self.tracked_agents.copy()
        
        for agent, interaction_type in copy_tracked_vehicles.items():
            other_agent = self.world.get_actor(agent)
            distance = self.vehicle.get_location().distance(other_agent.get_location())
            if distance > self.vehicle_tracking_radius:
                del self.tracked_agents[agent]
                pass



        
    # print(f'follow agent: {len(follow_agent)}')
    # print('vehicle at front: ', self.vehicle_at_front)






    # the idea of detecting intersection:
    # is intersection check what is the intersecting point between two global plans
    # if the intersection is a point then the 
    # global plan intersect in exactly one point 
    # the intersection type is a crossing in that case 

    # def set_interaction_type(self, agent):
    #     agent_global_plan = agent.get_global_plan()
    #     intersection = GeometryHelper.is_intersecting(self.global_plan, agent_global_plan)
    #     print(f'intersection: {len(intersection)}')
    #     if intersection.type == 'LineString':
    #         return InteractionType.NONCONFLICT
    #     if intersection.type == 'Point':
    #         return InteractionType.CROSS
    #     if intersection.type == 'MultiLineString':
    #         return InteractionType.FOLLOW
    #     if intersection.type == 'GeometryCollection':
    #         geom_list = list(intersection)
    #         for geom in geom_list:
    #             print(f'intersection type: {geom}')


            # if agent.local_map.road_list[0] == self.road_list[0]:
            #     return InteractionType.FOLLOW
            # else:
            #     return InteractionType.MERGE

        
        # print(f'intersection {intersection.type}')
        
        
        # pass




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
    





            # for agent, interaction_type in self.tracked_agents.items():
        #     if interaction_type == InteractionType.FOLLOW:
        #         follow_agent.append(agent)
        #     elif interaction_type == InteractionType.MERGE:
        #         merge_agent.append(agent)
        #     elif interaction_type == InteractionType.CROSS:
        #         cross_agent.append(agent)
        #     pass

        # min_distance = 9999
        # vehicle_at_front = None
        # print('follow agent list: ', follow_agent)
        # for agent in follow_agent:
        #     # print(f'agent: {agent}')
        #     other_follow_vehicle = self.world.get_actor(agent)
        #     # print(f'other follow vehicle: {other_follow_vehicle}')
        #     distance = self.vehicle.get_location().distance(other_follow_vehicle.get_location())
        #     if distance < min_distance:
        #         min_distance = distance
        #         vehicle_at_front = other_follow_vehicle
        
        # # print('vehicle at front: ', vehicle_at_front)
        # self.surrounding_agents['front'].update(ego_vehicle=self.vehicle, 
        #                                         other_vehicle=vehicle_at_front,
        #                                         del_t=del_t)
        
        
          