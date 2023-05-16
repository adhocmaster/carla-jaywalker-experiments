from enum import Enum
import statistics
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

TIME_STEP = 0.04

# CAR_FOLLOW_THW_LOWER = 0
# CAR_FOLLOW_THW_UPPER = 3

LC_MARGIN_SECOND = 5
LC_MARGIN_FRAMES = int(LC_MARGIN_SECOND/TIME_STEP)
TTC_STAR = 3

class Filter():
    
    @staticmethod
    def filter_dataframe(dataframe, *args):
        filtered_df = dataframe.copy()
        for i in range(0, len(args), 2):
            column_name = args[i]
            column_value = args[i + 1]
            print(f'Filtering by colName {column_name}, val {column_value}')
            if isinstance(column_value, tuple) or isinstance(column_value, list):
                min_value, max_value = column_value
                filtered_df = filtered_df[(filtered_df[column_name] >= min_value) & (filtered_df[column_name] <= max_value)]
            else:
                filtered_df = filtered_df[filtered_df[column_name] == column_value]
        print(f'Filtered dataframe from {len(dataframe)} to {len(filtered_df)} rows, ratio {len(filtered_df) / len(dataframe)}')
        return filtered_df

    # possible arg example. ('class', 'Car', 'lanechange', 0, )

    def _filter_actors(dataframe, *args):
        df = dataframe.copy()
        actors = df['id'].unique()
        nActors = len(actors)
        for i in range(0, len(args), 2):
            column_name = args[i]
            column_value = args[i + 1]

            if 'class' in column_name:
                filtered_actor_df = df[df[column_name] == column_value]
                filtered_actor = filtered_actor_df['id'].unique()

            if 'nLane' in column_name:
                grouped = df.groupby('id')
                filtered_actor = []
                for actor, group in grouped:
                    unique_lane_ids = group['laneId'].nunique()
                    if unique_lane_ids == column_value:
                        filtered_actor.append(actor)

            actors = np.intersect1d(actors, filtered_actor)

        print(f'total actors {nActors}, filtered actors {len(actors)}, ratio {len(actors) / nActors}')
        
        return actors

    @staticmethod
    def filter_vehicle_follow_scenario(dataframe, 
                                       ego_type, preceding_type, 
                                       minDuration, startDistance):
        print('Filtering vehicle follow scenario', ego_type, preceding_type, minDuration, startDistance)
        # this function returns a dataframe with only the lane follow data
        # start, end, ego_id, preceding_id

        car_following_meta = {'ego_id': [], 'preceding_id': [], 'start_frame': [], 'end_frame': [], 'duration': [], 'distance': []}

        # min duration is in seconds and 25 fps is the frame rate
        fps = 25
        frame_threshold = fps * minDuration if minDuration != -1 else 2

        fActor = Filter._filter_actors(dataframe, 
                                       'class', ego_type,
                                       'nLane', 1)
        pActor = Filter._filter_actors(dataframe,
                                      'class', preceding_type,
                                      'nLane', 1)

        # first find all the car-following scenarios
        for actor in fActor:
            actor_df = dataframe[dataframe['id'] == actor]
            preceding_id = list(set(actor_df['precedingId'].unique()) - {0})
            filtered_preceding_id = np.intersect1d(preceding_id, pActor)
            for p_id in filtered_preceding_id:
                frames_togather = actor_df[actor_df['precedingId'] == p_id]
                start_frame = frames_togather['frame'].iloc[0]
                end_frame = frames_togather['frame'].iloc[-1]
                ego_track = dataframe[(dataframe['id'] == actor) & (dataframe['frame'] == start_frame)].iloc[0]
                preceding_track = dataframe[(dataframe['id'] == p_id) & (dataframe['frame'] == start_frame)].iloc[0]
                startDistance = np.sqrt((ego_track['x'] - preceding_track['x']) ** 2 + (ego_track['y'] - preceding_track['y']) ** 2)

                car_following_meta['ego_id'].append(actor)
                car_following_meta['preceding_id'].append(p_id)
                car_following_meta['start_frame'].append(start_frame)
                car_following_meta['end_frame'].append(end_frame)
                car_following_meta['duration'].append((end_frame - start_frame)/fps)
                car_following_meta['distance'].append(startDistance)
        
        # filter by duration and distance
        all_scenario_df = pd.DataFrame(car_following_meta)
        filter_by_distance_duration = all_scenario_df[(all_scenario_df['distance'] >= startDistance) & (all_scenario_df['duration'] >= minDuration)]
        print(f'total scenario {len(all_scenario_df)}, filtered scenario {len(filter_by_distance_duration)}, ratio {len(filter_by_distance_duration) / len(all_scenario_df)}')
        return filter_by_distance_duration



    
