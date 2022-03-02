import carla 
from agents.navigation.controller import VehiclePIDController
from agents.vehicles.qnactr.Request import Request
from agents.vehicles.qnactr.map.LocalMap import LocalMap


from agents.vehicles.qnactr.servers.LongTermMemory import LongTermMemory
from agents.vehicles.qnactr.servers.ComplexCognition import ComplexCognition
from agents.vehicles.qnactr.servers.MotorControl import MotorControl
from agents.vehicles.qnactr.subtasks.LaneFollow import LaneFollow
from agents.vehicles.qnactr.subtasks.LaneKeeping import LaneKeeping
from .qnactr_enum import SubtaskType, ServerType



class CogModAgent():
    def __init__(self, id, vehicle, destination_point, driver_profile):
        if vehicle is None:
            raise ValueError('need to have vehicle')
            return

        self.id = id
        self.vehicle = vehicle
        self.destination_point = destination_point
        self.driver_profile = driver_profile
        self.server_settings = self.driver_profile['servers']
        self.local_map_settings = self.driver_profile['local_map']
        self.controller_settings = self.driver_profile['controller']
        self.subtask_settings = self.driver_profile['subtasks_parameters']
    

        self.world = self.vehicle.get_world()
        self.complete_map = self.world.get_map() 

        # set local map 
        print(f'vehicle location {self.vehicle.get_location()}')
        print(f'destination point: {self.destination_point}')
        self.local_map = self.set_local_map()

        # set servers cognitive servers
        self.longterm_memory, self.complex_cognition, self.motor_control = self.set_cognitive_servers()

        self.servers = [self.longterm_memory,
                        self.complex_cognition, 
                        self.motor_control]

        # cognitive server buffers
        self.retrieval_buffer = []
        self.computation_buffer = []
        self.motor_buffer = []

        # container for requests from different subtasks to be sent to cognitive servers
        # once sent, the request is removed from the container
        self.request_queue = []
        
        # initializing controller with PID parameters for applying vehicle control
        self.init_controller()
        # self.set_destination(self.destination_point)

        # creating subtasks
        self.lane_keeping_task = LaneKeeping(self.local_map)
        self.lane_following_task = LaneFollow(self.local_map)


        self.subtasks_queue = [self.lane_keeping_task, self.lane_following_task]


    def set_local_map(self):
        local_map = LocalMap(self.vehicle, self.destination_point,
                             self.local_map_settings['vehicle_tracking_radius'],
                             self.local_map_settings['global_plan_sampling_resolution'])
        return local_map

    def set_cognitive_servers(self):
        longterm_memory = LongTermMemory(self.server_settings['longterm_memory']['queue_length'],
                                         self.server_settings['longterm_memory']['tick_frequency'],
                                         self.subtask_settings)
        complex_cognition = ComplexCognition(self.server_settings['complex_cognition']['queue_length'],
                                             self.server_settings['complex_cognition']['tick_frequency']) 
        motor_control = MotorControl(self.server_settings['motor_control']['queue_length'],
                                     self.server_settings['motor_control']['tick_frequency']) 
        return longterm_memory, complex_cognition, motor_control  


    def init_controller(self):
        self._args_lateral_dict = self.controller_settings['lateral_PID']
        self._args_longitudinal_dict = self.controller_settings['longitudinal_PID'] 
        
        self._max_throt = self.controller_settings['max_throttle']
        self._max_brake = self.controller_settings['max_brake']
        self._max_steer = self.controller_settings['max_steering']
        self._offset = self.controller_settings['offset']

        self._vehicle_controller = VehiclePIDController(self.vehicle,
                                                        args_lateral=self._args_lateral_dict,
                                                        args_longitudinal=self._args_longitudinal_dict,
                                                        offset=self._offset,
                                                        max_throttle=self._max_throt,
                                                        max_brake=self._max_brake,
                                                        max_steering=self._max_steer)

        
    pass

    # at each step, the agent will:
    # 1. update the local map
    # 2. process requests from subtasks
    # 3. get response from the cognitive servers (long term memory, complex cognition, motor control)
    # 4. send ping to subtasks with the updated information from the buffers. (creates requests to servers)
    # 5. process requests from the subtasks

    def update_agent(self, global_agent_list):
        # # updating the local map with the current vehicle position
        # # calls the update function of the local map 
        self.update_local_map(global_agent_list)


        # calls the process_request function of the cognitive servers 
        self.process_request()

        # if any processing is done, the buffers will be updated with
        # the response from the servers. we read the buffers and store 
        # the responses in three separate buffers locally
        response_queue = self.get_response_from_buffers()

        # get all response for lane keeping subtask
        response_lane_keeping = []
        response_lane_following = []

        for response in response_queue:
            if response.receiver == SubtaskType.LANEKEEPING:
                response_lane_keeping.append(response)
            if response.receiver == SubtaskType.LANEFOLLOWING:
                response_lane_following.append(response)


        self.lane_keeping_task.onTick(self.local_map, response_lane_keeping)
        self.lane_following_task.onTick(self.local_map, response_lane_following)
        
        # get all response for lane keeping subtask
        subtask_requests = self.get_request_from_subtasks()

        self.send_request_to_servers(subtask_requests)

        # print(f'target velocity {self.motor_control.target_velocity}')
        # run one step of control using vehiclePIDController
        if self.motor_control.target_waypoint is not None and self.motor_control.target_velocity  != -1:
            control = self._vehicle_controller.run_step(target_speed=self.motor_control.target_velocity, 
                                                        waypoint=self.motor_control.target_waypoint)
            # self.vehicle.apply_control(control)
            
            return control






        # waypoint_req = Request(None, None, {'far_distance': 20, 'local_map': self.local_map})
        # next_waypoint = self.complex_cognition.get_next_waypoint(waypoint_req)

        # idm_param_dict = self.longterm_memory.get_idm_parameters()
        # velocity_req = Request(None, None, {'local_map': self.local_map, 'idm_parameters': idm_param_dict})
        # next_velocity = self.complex_cognition.get_next_velocity(velocity_req)

        # control = self._vehicle_controller.run_step(target_speed=next_velocity,
        #                                                 waypoint=next_waypoint)
        # self.vehicle.apply_control(control)

        # if self.motor_control.target_velocity  != -1:
        #     control = self._vehicle_controller.run_step(target_speed=self.motor_control.target_velocity,
        #                                                 waypoint=next_waypoint)
        #     self.vehicle.apply_control(control)

    


    def get_response_from_buffers(self):

        self.retrieval_buffer = self.longterm_memory.get_response()
        self.computation_buffer = self.complex_cognition.get_response()
        self.motor_buffer = self.motor_control.get_response()

        response_queue = self.get_responses_from_buffers()
        return response_queue

    def get_responses_from_buffers(self):
        response_queue = []
        if self.retrieval_buffer:
            for response in self.retrieval_buffer:
                response_queue.append(response)
        if self.computation_buffer:
            for response in self.computation_buffer:
                response_queue.append(response)
        if self.motor_buffer:
            for response in self.motor_buffer:
                response_queue.append(response)
        return response_queue




    # distribute the request to servers 
    def send_request_to_servers(self, subtask_requests):
        for request in subtask_requests:
            if request.receiver == ServerType.LONGTERM_MEMORY:
                self.longterm_memory.add_request(request)
            if request.receiver == ServerType.COMPLEX_COGNITION:
                self.complex_cognition.add_request(request)
            if request.receiver == ServerType.MOTOR_CONTROL:
                self.motor_control.add_request(request)


    # get requests from all the subtasks
    def get_request_from_subtasks(self):

        # get all requests from subtasks
        ret = []
        for subtask in self.subtasks_queue:
            req = subtask.get_request()
            for request in req:
                ret.append(request)
        for request in ret:
            print(str(request))
        return ret


    def get_vehicle_control(self):
        return self.vehicle.get_control()

    
    # def set_destination(self, destination):
    #     self.destination_point = destination
    #     self.local_map.set_global_plan(self.vehicle.get_transform(), self.destination_point)
    #     pass


    def process_request(self):
        for server in self.servers:
            server.process_request()
        pass


    def send_requests(self):
        for request in self.request_queue:
            if request.receiver == ServerType.LONGTERM_MEMORY:
                self.longterm_memory.add_request(request)
            if request.receiver == ServerType.COMPLEX_COGNITION:
                self.complex_cognition.add_request(request)
            if request.receiver == ServerType.MOTOR_CONTROL:
                self.motor_control.add_request(request)

        self.reset_request_queue()
        pass

    def reset_request_queue(self):
        self.request_queue = []
        pass
    
    
    def update_local_map(self, global_agent_list):
        other_agents = []
        for agent in global_agent_list:
            if agent.id != self.id:
                other_agents.append(agent)

        self.local_map.update(other_agents)
        pass

    def destroy(self):
        self.vehicle.destroy()
        pass

    def is_done(self):
        return self.local_map.is_done()



    

    