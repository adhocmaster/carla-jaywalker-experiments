
from .GazeSettings import *

CONST = 100
driver_profile = {
    # 'driver1': {
    #     'servers': {
    #         'longterm_memory': {'queue_length': 10, 'tick_frequency': 1,},
    #         'complex_cognition': {'queue_length': 10, 'tick_frequency': 1,},
    #         'motor_control': {'queue_length': 10, 'tick_frequency': 1,},
    #     },
    #     'local_map': {
    #         'vehicle_tracking_radius': 20,
    #         'global_plan_sampling_resolution': 1.0,
    #     },
    #     'gaze': Gaze_Settings1,
    #     'controller': {
    #         'lateral_PID': {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': 0.01,},
    #         'longitudinal_PID': {'K_P': 1.0, 'K_I': 0.05, 'K_D': 0.0, 'dt': 0.01,},
    #         'max_throttle': 0.75,
    #         'max_brake': 0.3,
    #         'max_steering': 0.8,
    #         'offset': 0.0,
    #     },
    #     'subtasks_parameters': {
    #         'lane_following': {
    #             'desired_velocity': 10.56, # m/s
    #             'safe_time_headway': 1.5, # s
    #             'max_acceleration': 2.73, # m/s^2
    #             'comfort_deceleration': 1.67, # m/s^2
    #             'acceleration_exponent': 4, 
    #             'minimum_distance': 4, # m
    #             'vehicle_length': 1, # m
    #         },
    #         'lane_keeping': {
    #             'far_distance': 30.0,
    #         },
    #     },
    # },

    'driver2': {
        'servers': {
            'longterm_memory': {'queue_length': 10, 'tick_frequency': 1,},
            'complex_cognition': {'queue_length': 10, 'tick_frequency': 1,},
            'motor_control': {'queue_length': 10, 'tick_frequency': 1,},
        },
        'local_map': {
            'vehicle_tracking_radius': CONST,                               # important parameter
            'global_plan_sampling_resolution': 1.0,               
        },
        'gaze': Gaze_Settings1,
        'controller': {
            'lateral_PID': {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': 0.04,},
            'longitudinal_PID': {'K_P': 1.5, 'K_I': 0.05, 'K_D': 0.01, 'dt': 0.04,},
            'max_throttle': 0.99,
            'max_brake': 0.5,
            'max_steering': 0.8,
            'offset': 0.0,
        },
        'subtasks_parameters': {
            'lane_following': {
                'desired_velocity': 14.12, # m/s
                'safe_time_headway': 0.37, # s
                'max_acceleration': 2.44, # m/s^2
                'comfort_deceleration': 0.68, # m/s^2
                'acceleration_exponent': 5, 
                'minimum_distance': 2, # m
                'vehicle_length': 4, # m
                'far_distance': CONST,                                 # important parameter
            },
            'lane_keeping': {
                'far_distance': CONST,                               # important parameter
            },
        },
    },

    # 'driver3': {
    #     'servers': {
    #         'longterm_memory': {'queue_length': 10, 'tick_frequency': 1,},
    #         'complex_cognition': {'queue_length': 10, 'tick_frequency': 1,},
    #         'motor_control': {'queue_length': 10, 'tick_frequency': 1,},
    #     },
    #     'local_map': {
    #         'vehicle_tracking_radius': 30,
    #         'global_plan_sampling_resolution': 1.0,
    #     },
    #     'controller': {
    #         'lateral_PID': {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': 0.01,},
    #         'longitudinal_PID': {'K_P': 1.0, 'K_I': 0.05, 'K_D': 0.0, 'dt': 0.01,},
    #         'max_throttle': 0.75,
    #         'max_brake': 0.3,
    #         'max_steering': 0.8,
    #         'offset': 0.0,
    #     },
    #     'subtasks_parameters': {
    #         'lane_following': {
    #             'desired_velocity': 5.56, # m/s
    #             'safe_time_headway': 1.5, # s
    #             'max_acceleration': 2.73, # m/s^2
    #             'comfort_deceleration': 1.67, # m/s^2
    #             'acceleration_exponent': 4, 
    #             'minimum_distance': 4, # m
    #             'vehicle_length': 1, # m
    #         },
    #         'lane_keeping': {
    #             'far_distance': 30.0,
    #         },
    #     },
    # },


    # 'driver4': {
    #     'servers': {
    #         'longterm_memory': {'queue_length': 10, 'tick_frequency': 2,},
    #         'complex_cognition': {'queue_length': 10, 'tick_frequency': 2,},
    #         'motor_control': {'queue_length': 10, 'tick_frequency': 1,},
    #     },
    #     'local_map': {
    #         'vehicle_tracking_radius': 30,
    #         'global_plan_sampling_resolution': 1.0,
    #     },
    #     'controller': {
    #         'lateral_PID': {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': 0.01,},
    #         'longitudinal_PID': {'K_P': 1.0, 'K_I': 0.05, 'K_D': 0.0, 'dt': 0.01,},
    #         'max_throttle': 0.75,
    #         'max_brake': 0.3,
    #         'max_steering': 0.8,
    #         'offset': 0.0,
    #     },
    #     'subtasks_parameters': {
    #         'lane_following': {
    #             'desired_velocity': 5.56, # m/s
    #             'safe_time_headway': 1.5, # s
    #             'max_acceleration': 2.73, # m/s^2
    #             'comfort_deceleration': 1.67, # m/s^2
    #             'acceleration_exponent': 4, 
    #             'minimum_distance': 4, # m
    #             'vehicle_length': 1, # m
    #         },
    #         'lane_keeping': {
    #             'far_distance': 30.0,
    #         },
    #     },
    # }
}