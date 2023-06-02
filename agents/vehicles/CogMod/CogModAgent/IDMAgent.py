import os
import logging
from .AgentInitializer import AgentIntializer
from .CognitiveModel.Subtasks.LaneKeeping import LaneKeeping
# from .CognitiveModel.Subtasks.LaneFollow import LaneFollow
from .RequestHandler import RequestHandler
from lib import LoggerFactory
from ..CogModEnum import ManeuverType
from .CognitiveModel.Subtasks.IntelligentDriverModel import IntelligentDriverModel

# time tracker for logging purpose
import time

class IDMAgent():
    def __init__(self, vehicle, destination_point, driver_profile):
        if vehicle is None:
            raise ValueError('need to have vehicle')
            return
        
        self.name = "IDMAgent"
        self.vehicle = vehicle
        self.world = vehicle.get_world()
        self.id = self.vehicle.id
        self.destination_point = destination_point

        self.driver_profile = driver_profile
        self.time_delta = 1.0
        
        self.driver_initializer = AgentIntializer(self.vehicle,
                                                  self.destination_point,
                                                  self.driver_profile)
        self.logLevel = logging.INFO
        self.logger = LoggerFactory.create(self.name, {'LOG_LEVEL':self.logLevel})

        self.local_map = self.driver_initializer.get_local_map()

        self.gaze = self.driver_initializer.get_gaze_module()

        self.servers_dict = self.driver_initializer.get_servers_dict()
        self.longterm_memory = self.driver_initializer.get_longterm_memory()
        self.complex_cognition = self.driver_initializer.get_complex_cognition()
        self.motor_control = self.driver_initializer.get_motor_control()

        self.vehicle_controller = self.driver_initializer.get_vehicle_controller()

        self.lane_keeping_task = LaneKeeping(self.local_map)
        # self.lane_following_task = LaneFollow(self.local_map)

        self.subtasks_queue = [self.lane_keeping_task]

        self.request_handler = RequestHandler(self.subtasks_queue, self.servers_dict, self.logLevel)
        
        self.counter = 0
        self.bigbang = time.time()
        
        
        
        # self.idm_parameters_dict = {
        #     'lane_following': {
        #                 'desired_velocity': 45 , # m/s
        #                 'safe_time_headway': 1.5, # s
        #                 'max_acceleration': 10, # m/s^2
        #                 'comfort_deceleration': 1.67, # m/s^2
        #                 'acceleration_exponent': 4, 
        #                 'minimum_distance': 2, # m
        #                 'vehicle_length': 1, # m
        #                 'far_distance': 500, # m
        #             }
        # }
        
        self.idm = IntelligentDriverModel(self.driver_profile['subtasks_parameters']['lane_following'],
                                          self.local_map,
                                          self.logger)
        # self.logger.info(f"CogModAgent is initialized {self.counter} system time {self.bigbang}")
        pass


    def get_vehicle(self):
        return self.vehicle

    def reset_driver(self, idm_paramters, time_delta=-1):
        # self.driver_initializer.reset_driver(driver_profile, time_delta)
        self.idm_parameters_dict = idm_paramters
        self.idm = IntelligentDriverModel(self.idm_parameters_dict['lane_following'],
                                          self.local_map,
                                          self.logger)
        self.time_delta = time_delta
        pass

    # depending on what the drivier is doing, we select a manuever type 
    def get_current_manuever(self):
        tracked_agent_manager = self.local_map.trackedAgentManager
        if tracked_agent_manager.is_there_vehicle('front'):
            return ManeuverType.VEHICLE_FOLLOW
        return ManeuverType.LANEFOLLOW


    # at each step, the agent will:
    # 1. detect the manuever type
    # 2. get gaze direction from distribution depending on the manuever type
    # 3. update local map with gaze direction and other static and dynamic elements
    # 4. process the existing requests in cognitive servers
    # 4.1 processed requests create responses 
    # 4.2 responses are stored in the buffers
    # 5. get responses from buffers
    # 6. send responses and local map to subtasks
    # 6.1 subtasks process the responses 
    # 6.2 subtasks create requests for the cognitive servers
    # 7. get requests from subtasks
    # 8. send requests to cognitive servers
    # 9. run one step of control using vehiclePIDController 
    #   if target velocity and waypoint are set

    def update_agent(self, global_vehicle_list, del_t):
        cur_time = time.time()
        self.counter += 1
        # self.logger.info(f"update_agent {self.counter}, {cur_time-self.bigbang}")
        manuever_type = self.get_current_manuever()

        # vehicle_inside_gaze_direction = self.gaze.filter_object_inside_gaze_direction(global_vehicle_list, manuever_type)
        # self.logger.info(f"vehicle: {vehicle_inside_gaze_direction}, dir {self.gaze.gaze_direction}")
        
        self.local_map.update(global_vehicle_list, del_t)

        self.request_handler.process_request_in_cognitive_servers()

        response_queue = self.request_handler.get_responses_from_buffers()

        self.request_handler.send_response_and_localmap_to_subtasks(response_queue, self.local_map)

        subtask_requests = self.request_handler.get_request_from_subtasks()

        self.request_handler.send_request_to_servers(subtask_requests)
        # self.logger.info(f"subtask state follow {self.lane_following_task.subtask_state}, keep {self.lane_keeping_task.subtask_state}")
        
        next_vel = self.idm.calc_velocity(self.time_delta)
        # print(f"next vel {next_vel}")
        self.motor_control.target_velocity = next_vel
        
        if self.motor_control.target_waypoint is not None and self.motor_control.target_velocity  != -1:
            control = self.vehicle_controller.run_step(target_speed=self.motor_control.target_velocity, 
                                                        waypoint=self.motor_control.target_waypoint)
            return control
        return None
    
    def get_vehicle_control(self):
        return self.vehicle.get_control()

    def destroy(self):
        self.vehicle.destroy()
        pass

    def is_done(self):
        return self.local_map.is_done()

    def run_step(self, del_t):
        actor_list = self.world.get_actors()
        global_actor_list = actor_list.filter("*vehicle*")
        filtered_vehicle_list = []
        for agent in global_actor_list:
            if agent.id != self.id:
                filtered_vehicle_list.append(agent)
        control = self.update_agent(filtered_vehicle_list, del_t)
        return control
