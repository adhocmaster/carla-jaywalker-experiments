
driver_profile = {
    'driver1': {
        'servers': {
            'longterm_memory': {'queue_length': 10, 'tick_frequency': 1,},
            'complex_cognition': {'queue_length': 10, 'tick_frequency': 1,},
            'motor_control': {'queue_length': 10, 'tick_frequency': 1,},
        },
        'local_map': {
            'vehicle_tracking_radius': 20,
            'global_plan_sampling_resolution': 1.0,
        },
        'controller': {
            'lateral_PID': {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': 0.01,},
            'longitudinal_PID': {'K_P': 1.0, 'K_I': 0.05, 'K_D': 0.0, 'dt': 0.01,},
            'max_throttle': 0.75,
            'max_brake': 0.3,
            'max_steering': 0.8,
            'offset': 0.0,
        },
        'subtasks_parameters': {
            'lane_following': {
                'desired_velocity': 3.5 , # m/s
                'safe_time_headway': 1.5, # s
                'max_acceleration': 0.73, # m/s^2
                'comfort_deceleration': 1.67, # m/s^2
                'acceleration_exponent': 4, 
                'minimum_distance': 2, # m
                'vehicle_length': 1, # m
            },
            'lane_keeping': {
                'far_distance': 15.0,
            },
        },
    },

    'driver2': {
        'servers': {
            'longterm_memory': {'queue_length': 10, 'tick_frequency': 10,},
            'complex_cognition': {'queue_length': 100, 'tick_frequency': 10,},
            'motor_control': {'queue_length': 10, 'tick_frequency': 1,},
        },
        'local_map': {
            'vehicle_tracking_radius': 10,
            'global_plan_sampling_resolution': 1.0,
        },
        'controller': {
            'lateral_PID': {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': 0.01,},
            'longitudinal_PID': {'K_P': 1.0, 'K_I': 0.05, 'K_D': 0.0, 'dt': 0.01,},
            'max_throttle': 0.75,
            'max_brake': 0.3,
            'max_steering': 0.8,
            'offset': 0.0,
        },
        'subtasks_parameters': {
            'lane_following': {
                'desired_velocity': 4.5 , # m/s
                'safe_time_headway': 1.5, # s
                'max_acceleration': 0.73, # m/s^2
                'comfort_deceleration': 1.67, # m/s^2
                'acceleration_exponent': 4, 
                'minimum_distance': 2, # m
                'vehicle_length': 1, # m
            },
            'lane_keeping': {
                'far_distance': 15.0,
            },
        },
    },

    'driver3': {
        'servers': {
            'longterm_memory': {'queue_length': 10, 'tick_frequency': 1,},
            'complex_cognition': {'queue_length': 10, 'tick_frequency': 1,},
            'motor_control': {'queue_length': 10, 'tick_frequency': 1,},
        },
        'local_map': {
            'vehicle_tracking_radius': 30,
            'global_plan_sampling_resolution': 1.0,
        },
        'controller': {
            'lateral_PID': {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': 0.01,},
            'longitudinal_PID': {'K_P': 1.0, 'K_I': 0.05, 'K_D': 0.0, 'dt': 0.01,},
            'max_throttle': 0.75,
            'max_brake': 0.3,
            'max_steering': 0.8,
            'offset': 0.0,
        },
        'subtasks_parameters': {
            'lane_following': {
                'desired_velocity': 5.5 , # m/s
                'safe_time_headway': 1.5, # s
                'max_acceleration': 0.73, # m/s^2
                'comfort_deceleration': 1.67, # m/s^2
                'acceleration_exponent': 4, 
                'minimum_distance': 5, # m
                'vehicle_length': 1, # m
            },
            'lane_keeping': {
                'far_distance': 15.0,
            },
        },
    },


    'fast_reckless_driver': {
        'servers': {
            'longterm_memory': {'queue_length': 10, 'tick_frequency': 1,},
            'complex_cognition': {'queue_length': 10, 'tick_frequency': 1,},
            'motor_control': {'queue_length': 10, 'tick_frequency': 1,},
        },
        'local_map': {
            'vehicle_tracking_radius': 60,
            'global_plan_sampling_resolution': 1.0,
        },
        'controller': {
            'lateral_PID': {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': 0.01,},
            'longitudinal_PID': {'K_P': 1.0, 'K_I': 0.05, 'K_D': 0.0, 'dt': 0.01,},
            'max_throttle': 0.9,
            'max_brake': 0.6,
            'max_steering': 0.8,
            'offset': 0.0,
        },
        'subtasks_parameters': {
            'lane_following': {
                'desired_velocity': 7.5, # m/s
                'safe_time_headway': 0.5, # s
                'max_acceleration': 0.83, # m/s^2
                'comfort_deceleration': 1.97, # m/s^2
                'acceleration_exponent': 2, 
                'minimum_distance': 2, # m
                'vehicle_length': 1, # m
            },
            'lane_keeping': {
                'far_distance': 20.0,
            },
        },
    },


    'DOM': {
        'servers': {
            'longterm_memory': {'queue_length': 10, 'tick_frequency': 1,},
            'complex_cognition': {'queue_length': 10, 'tick_frequency': 1,},
            'motor_control': {'queue_length': 10, 'tick_frequency': 1,},
        },
        'local_map': {
            'vehicle_tracking_radius': 100,
            'global_plan_sampling_resolution': 2.0,
        },
        'controller': {
            'lateral_PID': {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': 0.01,},
            'longitudinal_PID': {'K_P': 1.0, 'K_I': 0.05, 'K_D': 0.0, 'dt': 0.01,},
            'max_throttle': 0.9,
            'max_brake': 0.6,
            'max_steering': 0.8,
            'offset': 0.0,
        },
        'subtasks_parameters': {
            'lane_following': {
                'desired_velocity': 15.5, # m/s
                'safe_time_headway': 0.5, # s
                'max_acceleration': 1.83, # m/s^2
                'comfort_deceleration': 2.97, # m/s^2
                'acceleration_exponent': 6, 
                'minimum_distance': 1, # m
                'vehicle_length': 1, # m
            },
            'lane_keeping': {
                'far_distance': 20.0,
            },
        },
    },

    'slow_driver': {
        'servers': {
            'longterm_memory': {'queue_length': 1, 'tick_frequency': 10,},
            'complex_cognition': {'queue_length': 1, 'tick_frequency': 10,},
            'motor_control': {'queue_length': 10, 'tick_frequency': 1,},
        },
        'local_map': {
            'vehicle_tracking_radius': 20,
            'global_plan_sampling_resolution': 1.0,
        },
        'controller': {
            'lateral_PID': {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': 0.01,},
            'longitudinal_PID': {'K_P': 1.0, 'K_I': 0.05, 'K_D': 0.0, 'dt': 0.01,},
            'max_throttle': 0.75,
            'max_brake': 0.3,
            'max_steering': 0.8,
            'offset': 0.0,
        },
        'subtasks_parameters': {
            'lane_following': {
                'desired_velocity': 9.5 , # m/s
                'safe_time_headway': 1.5, # s
                'max_acceleration': 0.73, # m/s^2
                'comfort_deceleration': 1.67, # m/s^2
                'acceleration_exponent': 4, 
                'minimum_distance': 2, # m
                'vehicle_length': 1, # m
            },
            'lane_keeping': {
                'far_distance': 15.0,
            },
        },
    },

}