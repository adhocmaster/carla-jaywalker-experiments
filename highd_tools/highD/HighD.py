import pandas as pd


from .DataContainer import DataContainer
from .Visual import Visualizer
from .ManeuverFilter import *
from .config import *
from .HighDStats import HighDStats

class HighD:
    def __init__(self, 
                 data_container: DataContainer):
        
        self.id = data_container.id

        self.image = data_container.image
        self.recordingMeta = data_container.recordingMeta
        self.tracksMeta = data_container.tracksMeta
        self.tracks = data_container.tracks

        self.recordingMeta_dict = data_container.recordingMeta_dict
        self.tracksMeta_dict = data_container.tracksMeta_dict
        self.track_dict = data_container.tracks_dict

        self.output_path = OUTPUT_DIRECTORY

        self.highD_stats = HighDStats(data_container)

        self.car_follow = None
        self.lane_change = None

        pass

    def get_highway_image(self):
        return self.image

    def get_recordingMeta(self):
        return self.recordingMeta

    def get_tracksMeta(self):
        return self.tracksMeta
    
    def get_tracks(self):
        return self.tracks

    def get_nFrame_follow_scenario(self, thw_lower_bound, thw_upper_bound, time_duration, distance_threshold, follow_type):
        follow_meta = self.get_vehicle_follow_meta(thw_lower_bound, thw_upper_bound, time_duration, distance_threshold) # 0 is for distance threshold        
        follow_interaction_type = self.get_follow_interaction_type(follow_type)
        follow_meta = follow_meta[follow_meta['followType'] == follow_interaction_type]
        return self.highD_stats.nFrames_vehicle_follow(follow_meta)

    def follow_distance_distribution(self, thw_lower_bound, thw_upper_bound, duration_threshold, distance_threshold, follow_type):
        follow_meta = self.get_vehicle_follow_meta(thw_lower_bound, thw_upper_bound, duration_threshold, distance_threshold) # 0 is for distance threshold
        print('follow meta : ', len(follow_meta))
        follow_interaction_type = self.get_follow_interaction_type(follow_type)
        follow_meta = follow_meta[follow_meta['followType'] == follow_interaction_type]
        self.highD_stats.follow_distance_distribution(follow_meta)
        pass

    def follow_relative_speed_distribution(self, thw_lower_bound, thw_upper_bound, duration_threshold, distance_threshold, follow_type):
        follow_meta = self.get_vehicle_follow_meta(thw_lower_bound, thw_upper_bound, duration_threshold, distance_threshold) # 0 is for distance threshold
        follow_interaction_type = self.get_follow_interaction_type(follow_type)
        follow_meta = follow_meta[follow_meta['followType'] == follow_interaction_type]
        self.highD_stats.follow_relative_speed_distribution(follow_meta)
        pass

    def follow_speed_distance_ratio(self, thw_lower_bound, thw_upper_bound, duration_threshold, distance_threshold, follow_type):
        follow_meta = self.get_vehicle_follow_meta(thw_lower_bound, thw_upper_bound, duration_threshold, distance_threshold) # 0 is for distance threshold
        follow_interaction_type = self.get_follow_interaction_type(follow_type)
        follow_meta = follow_meta[follow_meta['followType'] == follow_interaction_type]
        self.highD_stats.follow_speed_distance_ratio(follow_meta)
        pass

    def get_follow_interaction_type(self, follow_type):
        follow_interaction_type = None
        if follow_type == "car_car":
            follow_interaction_type = FollowType.CAR_CAR
        elif follow_type == "car_truck":
            follow_interaction_type = FollowType.CAR_TRUCK
        elif follow_type == "truck_truck":
            follow_interaction_type = FollowType.TRUCK_TRUCK
        elif follow_type == "truck_car":
            follow_interaction_type = FollowType.TRUCK_CAR
        return follow_interaction_type

    

    def draw_frame(self, frame_id, ego_id, target_id, ego_color, target_color):
        
        # print(self.tracks)
        data = Visualizer.draw_frame(image=self.image,
                                     tracks=self.tracks,
                                     frame_id=frame_id,
                                     ego_id=ego_id,
                                     target_id=target_id,
                                     ego_color=ego_color,
                                     target_color=target_color)

        return data

    def create_and_save_video_from_frames(self, start, end, fps=25, video_name=None):
        Visualizer.create_video_from_frames(image=self.image,
                                            tracks=self.tracks,
                                            start=start,
                                            end=end,
                                            fps=fps,
                                            video_name=video_name,
                                            output_dir=self.output_path)
        pass

    def create_and_save_video_for_agent(self, agent_id, fps=25, video_name=None):
        Visualizer.create_video_for_agent(image=self.image,
                                          tracks=self.tracks,
                                          tracksMeta=self.tracksMeta,
                                          agent_id=agent_id,
                                          fps=fps,
                                          video_name=video_name,
                                          output_dir=self.output_path)
        pass


    def create_and_save_video_with_two_agents(self, agent_id, target_id, fps=25, video_name=None):
        Visualizer.create_video_with_two_agents(image=self.image,
                                                tracks=self.tracks,
                                                tracksMeta=self.tracksMeta,
                                                agent_id=agent_id,
                                                target_id=target_id,
                                                fps=fps,
                                                video_name=video_name,
                                                output_dir=self.output_path)
        pass


    # This function filters the car vehicle following scenarios 
    # total 4 types of interaction is possible between two vehicles
    # (Car, Car), (Car, Truck), (Truck, Car), (Truck, Truck)
    
    def get_vehicle_follow_meta(self, thw_lower_bound, thw_upper_bound, time_duration=-1, distance_threshold=100):
        
        df = pd.DataFrame()
        # enumarate over all followtype enum
        car_car_follow = find_vehicle_following_meta(self.tracksMeta,
                                                 self.tracks,
                                                 ego_type="Car",
                                                 preceding_type="Car",
                                                 thw_lower_bound=thw_lower_bound,
                                                 thw_upper_bound=thw_upper_bound,
                                                 min_duration=time_duration,
                                                 distance_threshold=distance_threshold)
        car_car_follow = pd.DataFrame(car_car_follow)
        car_car_follow["followType"] = FollowType.CAR_CAR

        car_truck_follow = find_vehicle_following_meta(self.tracksMeta,
                                                   self.tracks,
                                                    ego_type="Car",
                                                    preceding_type="Truck",
                                                    thw_lower_bound=thw_lower_bound,
                                                    thw_upper_bound=thw_upper_bound,
                                                    min_duration=time_duration,
                                                    distance_threshold=distance_threshold)
        car_truck_follow = pd.DataFrame(car_truck_follow)
        car_truck_follow["followType"] = FollowType.CAR_TRUCK

        truck_car_follow = find_vehicle_following_meta(self.tracksMeta,
                                                   self.tracks,
                                                   ego_type="Truck",
                                                    preceding_type="Car",
                                                    thw_lower_bound=thw_lower_bound,
                                                    thw_upper_bound=thw_upper_bound,
                                                    min_duration=time_duration,
                                                    distance_threshold=distance_threshold)
        truck_car_follow = pd.DataFrame(truck_car_follow)
        truck_car_follow["followType"] = FollowType.TRUCK_CAR

        truck_truck_follow = find_vehicle_following_meta(self.tracksMeta,
                                                        self.tracks,
                                                        ego_type="Truck",
                                                        preceding_type="Truck",
                                                        thw_lower_bound=thw_lower_bound,
                                                        thw_upper_bound=thw_upper_bound,
                                                        min_duration=time_duration,
                                                        distance_threshold=distance_threshold)
        truck_truck_follow = pd.DataFrame(truck_truck_follow)
        truck_truck_follow["followType"] = FollowType.TRUCK_TRUCK

        follow_meta = pd.concat([car_car_follow, car_truck_follow, truck_car_follow, truck_truck_follow])
        return follow_meta



    # def filter_lane_change(self):
    #     self.lane_change = get_lane_change_trajectory(self.tracksMeta_dict, self.track_dict)
    #     return self.lane_change

    # def lane_change_stats(self):
    #     result = find_lane_changes(self.tracksMeta_dict, self.track_dict)
    #     return result


#     def split_dataset(self):
#         df = self.tracksMeta
#         l2r = df.loc[(df["drivingDirection"] == 1)]
#         r2l = df.loc[(df["drivingDirection"] == 2)]

#         agent_l2r = l2r['id'].values
#         agent_r2l = r2l['id'].values

#         l2r_df = self.tracks.loc[(self.tracks["id"].isin(agent_l2r))]
#         r2l_df = self.tracks.loc[(self.tracks["id"].isin(agent_r2l))]
        
#         return l2r_df, r2l_df


