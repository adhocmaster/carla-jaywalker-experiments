from .CogModController import VehiclePIDController
from .CogModVision.Gaze import Gaze
from .CognitiveModel.Map import LocalMap 
from .CognitiveModel.Servers import LongTermMemory, ComplexCognition, MotorControl
from ..CogModEnum import ServerType



class AgentIntializer():
    def __init__(self, 
                 vehicle,
                 destination,
                 driver_profile):

        self.driver_profile = driver_profile
        self.vehicle = vehicle
        self.destination = destination
        
        # print('driver profile ', self.driver_profile, vehicle, destination)

        self.server_settings = self.driver_profile['servers']
        self.local_map_settings = self.driver_profile['local_map']
        self.gaze_settings = self.driver_profile['gaze']
        self.controller_settings = self.driver_profile['controller']
        self.subtask_settings = self.driver_profile['subtasks_parameters'] 

        self.local_map = self.set_local_map()

        self.servers_dict = self.set_cognitive_servers()
        self.longterm_memory = self.servers_dict[ServerType.LONGTERM_MEMORY]
        self.complex_cognition = self.servers_dict[ServerType.COMPLEX_COGNITION]
        self.motor_control = self.servers_dict[ServerType.MOTOR_CONTROL]

        self.vehicle_controller = self.set_pid_controllers()

        self.gaze = self.set_gaze_module()

        pass

    def reset_driver(self, driver_profile):
        self.driver_profile = driver_profile
        self.servers_dict = self.set_cognitive_servers()
        self.longterm_memory = self.servers_dict[ServerType.LONGTERM_MEMORY]
        self.complex_cognition = self.servers_dict[ServerType.COMPLEX_COGNITION]
        self.motor_control = self.servers_dict[ServerType.MOTOR_CONTROL]
        pass
    
    def set_local_map(self):
        print(f'agent tracking radius {self.local_map_settings["vehicle_tracking_radius"]}')
        local_map = LocalMap(self.vehicle,
                             self.destination,
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
        
        ret_dict = {ServerType.LONGTERM_MEMORY : longterm_memory, 
                    ServerType.COMPLEX_COGNITION : complex_cognition, 
                    ServerType.MOTOR_CONTROL : motor_control} 
        return ret_dict

    def set_pid_controllers(self):

        self._args_lateral_dict = self.controller_settings['lateral_PID']
        self._args_longitudinal_dict = self.controller_settings['longitudinal_PID'] 
        
        self._max_throt = self.controller_settings['max_throttle']
        self._max_brake = self.controller_settings['max_brake']
        self._max_steer = self.controller_settings['max_steering']
        self._offset = self.controller_settings['offset']

        self.vehicle_controller = VehiclePIDController(self.vehicle,
                                                        args_lateral=self._args_lateral_dict,
                                                        args_longitudinal=self._args_longitudinal_dict,
                                                        offset=self._offset,
                                                        max_throttle=self._max_throt,
                                                        max_brake=self._max_brake,
                                                        max_steering=self._max_steer)

        return self.vehicle_controller

    def set_gaze_module(self):
        self.gaze = Gaze(self.vehicle, self.gaze_settings)
        return self.gaze

    def get_servers_dict(self):
        return self.servers_dict

    def get_local_map(self):
        return self.local_map

    def get_longterm_memory(self):
        return self.longterm_memory
    
    def get_complex_cognition(self):
        return self.complex_cognition

    def get_motor_control(self):
        return self.motor_control

    def get_vehicle_controller(self):
        return self.vehicle_controller
    
    def get_gaze_module(self):
        return self.gaze