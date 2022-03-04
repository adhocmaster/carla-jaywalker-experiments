
# 1 -> (-17, 44) 
# 2 -> (-21, 44)
# 3 -> (12, 13) 
# 4 -> (12, 16) 
# 5 -> (-49, 12)
# 6 -> (-49, 16) 
# 7 -> (-17, 30)



#   A
# 
# |   |
# |3 4|
# |   |
# |   L________________
# |      7    1          # B
# |    _______2________
# |   |
# |   |
# |5 6|
# 
#   C


# (-17, 44) -> (12, 16), (-49, 12)
# (12, 13)  -> (-49, 12), (-21, 44)
# (-49, 16) -> (-21, 44), (12, 16)

from .driver_profile import driver_profile
from .trajctory_follower_settings import trajectory_follower_settings

t_junction_settings = {


# settings with single vehicle 

    # A to straight to C
    "setting1": {
        "cogmod_agents": {
            "number_of_cogmod_agents": 1,
            "1": {
                "spawn_point": (12, 13), # 3
                "destination_point": (-49, 12), # 5
                "driver_profile": driver_profile["slow_driver"],
            },
        },
        "actor_agents": {
            "number_of_actor_agents": 1,
            "1": {
                "trajectory": trajectory_follower_settings["trajectory1"],
            }
        }
    },

#     # A to left turn to B
#     "setting2": { 
#         "number_of_cogmod_agents": 1,
#         "1": {
#             "spawn_point": (12, 13), # 3
#             "destination_point": (-21, 44), # 2
#             "driver_profile": driver_profile["DOM"],
#         },
#     },

#     # B to left turn to C
#     "setting3": { 
#         "number_of_cogmod_agents": 1,
#         "1": {
#             "spawn_point": (-17, 44), # 1
#             "destination_point": (-49, 12), # 5
#             "driver_profile": driver_profile["DOM"],
#         },
#     },

#     # B to right turn to A
#     "setting4": { 
#         "number_of_cogmod_agents": 1,
#         "1": {
#             "spawn_point": (-17, 44), # 1
#             "destination_point": (12, 16), # 4
#             "driver_profile": driver_profile["DOM"],
#         },
#     },
    
#     # C to straight to A
#     "setting5": { 
#         "number_of_cogmod_agents": 1,
#         "1": {
#             "spawn_point": (-49, 16), # 6
#             "destination_point": (12, 16), # 4
#             "driver_profile": driver_profile["DOM"],
#         },
#     },
#     # C to right turn to B
#     "setting6": { 
#         "number_of_cogmod_agents": 1,
#         "1": {
#             "spawn_point": (-49, 16), # 6
#             "destination_point": (-21, 44), # 2
#             "driver_profile": driver_profile["DOM"],
#         },
#     },

# # settings with two vehicles

#     # 1 A to straight to C
#     # 2 B to right turn to A
#     "setting7": { 
#         "number_of_cogmod_agents": 2,
#         "1": {
#             "spawn_point": (12, 13), # 3
#             "destination_point": (-49, 12), # 5
#             "driver_profile": driver_profile["DOM"],
#         },
#         "2": {
#             "spawn_point": (-17, 44), # 1
#             "destination_point": (12, 16), # 4
#             "driver_profile": driver_profile["DOM"],
#         },
#     },
#     # 1 A to straight to C
#     # 2 B to left turn to C
#     "setting8": { 
#         "number_of_cogmod_agents": 2,
#         "1": {
#             "spawn_point": (12, 13), # 3
#             "destination_point": (-49, 12), # 5
#             "driver_profile": driver_profile["fast_reckless_driver"],
#         },
#         "2": {
#             "spawn_point": (-17, 44), # 1
#             "destination_point": (-49, 12), # 5
#             "driver_profile": driver_profile["DOM"],
#         },
#     },

#     # 1 A to left turn to B
#     # 2 B to left turn to C
#     "setting9": { 
#         "number_of_cogmod_agents": 2,
#         "1": {
#             "spawn_point": (12, 13), # 3
#             "destination_point": (-21, 44), # 2
#             "driver_profile": driver_profile["DOM"],
#         },
#         "2": {
#             "spawn_point": (-17, 44), # 1
#             "destination_point": (-49, 12), # 5
#             "driver_profile": driver_profile["DOM"],
#         },
#     },

#     # 1 B to left turn to C
#     # 2 B (ahead) to left turn to C
#     "setting10": { 
#         "number_of_cogmod_agents": 2,
#         "1": {
#             "spawn_point": (-17, 44), # 1
#             "destination_point": (-49, 12), # 5
#             "driver_profile": driver_profile["DOM"],
#         },
#         "2": {
#             "spawn_point": (-17, 30), # 3
#             "destination_point": (-49, 12), # 2
#             "driver_profile": driver_profile["slow_driver"],
#         },

#     },

#     # 1 C to straight to A
#     # 2 A to straight to C
#     "setting11": { 
#         "number_of_cogmod_agents": 2,
#         "1": {
#             "spawn_point": (-49, 16), # 6
#             "destination_point": (12, 16), # 4
#             "driver_profile": driver_profile["driver1"],
#         },
#         "2": {
#             "spawn_point": (12, 13), # 3
#             "destination_point": (-49, 12), # 5
#             "driver_profile": driver_profile["driver2"],
#         },
#     },


#     # 1 A to straight to C
#     # 2 A (ahead) to straight to C
#     "setting12": { 
#         "number_of_cogmod_agents": 2,
#         "1": {
#             "spawn_point": (12, 13), # 3
#             "destination_point": (-49, 12), # 5
#             "driver_profile": driver_profile["driver1"],
#         },
#         "2": {
#             "spawn_point": (0, 13), # 3 (ahead)
#             "destination_point": (-49, 12), # 5
#             "driver_profile": driver_profile["slow_driver"],
#         },
#     },

#     # # 1 A to straight to C
#     # # 2 B to right turn to A
#     # "setting12": { 
#     #     "number_of_agents": 2,
#     #     "1": {
#     #         "spawn_point": (12, 13), # 3
#     #         "destination_point": (-49, 12), # 5
#     #         "driver_profile": driver_profile["driver2"],
#     #     },
#     #     "2": {
#     #         "spawn_point": (-17, 44), # 1
#     #         "destination_point": (12, 16), # 4
#     #         "driver_profile": driver_profile["driver3"],
#     #     },
#     # },

# #     # 1 from B to left turn to C
# #     # 2 from A to left turn to B
# #     # 3 from B (ahead) to left turn to C
# #     "setting7": { 
# #         "number_of_agents": 3,
# #         "1": {
# #             "spawn_point": (-17, 44), # 1
# #             "destination_point": (-49, 12), # 5
# #             "driver_profile": driver_profile["driver1"],
# #         },
# #         "2": {
# #             "spawn_point": (12, 13), # 3
# #             "destination_point": (-21, 44), # 2
# #             "driver_profile": driver_profile["driver2"],
# #         },
# #         "3": {
# #             "spawn_point": (-17, 30), # 3
# #             "destination_point": (-49, 12), # 2
# #             "driver_profile": driver_profile["driver3"],
# #         },

# #     },

}






