from lib.MapManager import MapNames
import carla
from agents.vehicles.CogMod.Settings.DriverSettings import driver_profile

scenarios = {
    # "scenario1": {
    #     "map": MapNames.HighWay_Ring,
    #     "cogmod_agent": {
    #         "source": carla.Location(x=-213, y=6, z=0.5),
    #         "destination": carla.Location(x=570, y=3, z=0.5),
    #         "driver_profile": driver_profile['driver2']
    #     },
    #     "actor_agent": {
    #         "source": carla.Location(x=-170, y=6, z=0.5),
    #         "destination": carla.Location(x=570, y=3, z=0.5),
    #         "driver_profile": 'normal',
    #         "target_speed": 8
    #     },
    #     "trigger_distance": 20
    # },
    # "scenario2": {
    #     "map": MapNames.HighWay_Ring,
    #     "cogmod_agent": {
    #         "source": carla.Location(x=-215, y=7, z=1.5),
    #         "destination": carla.Location(x=570, y=7, z=1.5),
    #         "driver_profile": driver_profile['driver1']
    #     },
    #     # "actor_agent": {
    #     #     "source": carla.Location(x=-215, y=3, z=1.5),
    #     #     "destination": carla.Location(x=510, y=3, z=1.5),
    #     #     "driver_profile": 'normal',
    #     #     "target_speed": 10
    #     # },
    #     "trigger_distance": 20
    # },

    # "scenario3": {
    #     "map": MapNames.HighWay_Ring,
    #     "high_d_path": f"C:\\Users\\abjawad\\Documents\\GitHub\\cogmod-driver-behavior-model\\agents\\vehicles\\TrajectoryAgent\\tracks.csv",
    #     "stable_height_path": f"C:\\Users\\abjawad\\Documents\\GitHub\\cogmod-driver-behavior-model\\settings\\stable_height.csv",
    #     "lane_id": {
    #         "left_lane":[4, 5, 6],
    #         "right_lane":[2,3],
    #     },
    #     "pivot": carla.Transform(carla.Location(x=0, y=-22, z=0)),
    # },

    "scenario4": {
        "map": MapNames.HighWay_Ring,
        "high_d_path": f'D:\\highD_data\\highD_dataset',
        "dataset_id": '01',
        "stable_height_path": f"C:\\Users\\abjawad\\Documents\\GitHub\\cogmod-driver-behavior-model\\settings\\stable_height.csv",
        "lane_id": {
            # ---------------
            # ------ < ------ direction of look ahead
            # ---------------
            "left_lane":[4, 5, 6],
            "right_lane":[2,3],
        },
        "pivot": carla.Transform(carla.Location(x=0, y=-22, z=0)),
        "car_follow_settings":{
            'ego_type': 'Car',
            'preceding_type': 'Car',
            'time_duration': 5,
            'distance_threshold': 50,
        },
        "base_distance": 800,
        "cogmod_agent": {
            "source": None,
            "destination": None,
            "driver_profile": driver_profile['driver2']
        },
    },
}



