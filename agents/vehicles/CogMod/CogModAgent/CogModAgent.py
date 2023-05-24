import os
import logging
from .AgentInitializer import AgentIntializer
from .CognitiveModel.Subtasks.LaneKeeping import LaneKeeping
from .CognitiveModel.Subtasks.LaneFollow import LaneFollow
from .RequestHandler import RequestHandler
from lib import LoggerFactory
from ..CogModEnum import ManeuverType

# time tracker for logging purpose
import time

class CogModAgent():
    def __init__(self, vehicle, destination_point, driver_profile):
        if vehicle is None:
            raise ValueError('need to have vehicle')
            return
        
        self.name = "CogModAgent"
        self.vehicle = vehicle
        self.world = vehicle.get_world()
        self.id = self.vehicle.id
        self.destination_point = destination_point

        self.driver_profile = driver_profile
        self.driver_initializer = AgentIntializer(self.vehicle,
                                                  self.destination_point,
                                                  self.driver_profile)
        
        self.logger = LoggerFactory.create(self.name, {'LOG_LEVEL':logging.ERROR})

        self.local_map = self.driver_initializer.get_local_map()

        self.gaze = self.driver_initializer.get_gaze_module()

        self.servers_dict = self.driver_initializer.get_servers_dict()
        self.longterm_memory = self.driver_initializer.get_longterm_memory()
        self.complex_cognition = self.driver_initializer.get_complex_cognition()
        self.motor_control = self.driver_initializer.get_motor_control()

        self.vehicle_controller = self.driver_initializer.get_vehicle_controller()

        self.lane_keeping_task = LaneKeeping(self.local_map)
        self.lane_following_task = LaneFollow(self.local_map)

        self.subtasks_queue = [self.lane_following_task, self.lane_keeping_task]

        self.request_handler = RequestHandler(self.subtasks_queue, self.servers_dict)
        
        self.counter = 0
        self.bigbang = time.time()
        self.logger.info(f"CogModAgent is initialized {self.counter} system time {self.bigbang}")
        pass


    def get_vehicle(self):
        return self.vehicle

    def reset_driver(self, driver_profile):
        self.driver_initializer.reset_driver(driver_profile)
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
        self.logger.info(f"update_agent {self.counter}, {cur_time-self.bigbang}")
        manuever_type = self.get_current_manuever()

        vehicle_inside_gaze_direction = self.gaze.filter_object_inside_gaze_direction(global_vehicle_list, manuever_type)
        self.logger.info(f"vehicle: {vehicle_inside_gaze_direction}, dir {self.gaze.gaze_direction}")
        
        self.local_map.update(vehicle_inside_gaze_direction, del_t)

        self.request_handler.process_request_in_cognitive_servers()

        response_queue = self.request_handler.get_responses_from_buffers()

        self.request_handler.send_response_and_localmap_to_subtasks(response_queue, self.local_map)

        subtask_requests = self.request_handler.get_request_from_subtasks()

        self.request_handler.send_request_to_servers(subtask_requests)
        self.logger.info(f"subtask state follow {self.lane_following_task.subtask_state}, keep {self.lane_keeping_task.subtask_state}")
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
