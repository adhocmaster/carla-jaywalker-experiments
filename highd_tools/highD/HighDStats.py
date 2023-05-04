
import pandas as pd
from .PlotHelper import Histogram
from .ManeuverFilter import *


# this class provides statistics for a single highD dataset 
# the location of vehicle (x, y) are the top left corner of the vehicle !!!Important!!!

class HighDStats():
    def __init__(self, DataContainer):

        self.data_container = DataContainer
        # print("Inside HighD again stats")       
        pass
    
    # we plot the velocity of both the vehicle and the preceding vehicle
    def plot_agent_following_scenario(self, follow_meta):
        tracks = self.data_container.tracks

        ego_id = follow_meta['ego_id']
        preceding_id = follow_meta['preceding_id']
        start_frame = follow_meta['start_frame']
        end_frame = follow_meta['end_frame']

        title = f"Scenario {ego_id} - {preceding_id} - {end_frame - start_frame}"

        plot_dict = {
            'frame': [],
            'ego_speed': [],
            'preceding_speed': [],
            'relative_speed': [],
            'relative_distance': [],
            'ttc_ego':[],
            'thw_ego':[],
            'dhw_ego':[],
        }

        for frame in range(start_frame, end_frame):
            ego_speed = abs(tracks[(tracks['id'] == ego_id) & (tracks['frame'] == frame)]['xVelocity'].values[0])
            preceding_speed = abs(tracks[(tracks['id'] == preceding_id) & (tracks['frame'] == frame)]['xVelocity'].values[0])
            relative_speed = ego_speed - preceding_speed

            ego_x = tracks[(tracks['id'] == ego_id) & (tracks['frame'] == frame)]['x'].values[0]
            ego_y = tracks[(tracks['id'] == ego_id) & (tracks['frame'] == frame)]['y'].values[0]
            preceding_x = tracks[(tracks['id'] == preceding_id) & (tracks['frame'] == frame)]['x'].values[0]
            preceding_y = tracks[(tracks['id'] == preceding_id) & (tracks['frame'] == frame)]['y'].values[0]
            relative_distance = np.sqrt((ego_x - preceding_x)**2 + (ego_y - preceding_y)**2)

            ttc_ego = tracks[(tracks['id'] == ego_id) & (tracks['frame'] == frame)]['ttc'].values[0]
            thw_ego = tracks[(tracks['id'] == ego_id) & (tracks['frame'] == frame)]['thw'].values[0]
            dhw_ego = tracks[(tracks['id'] == ego_id) & (tracks['frame'] == frame)]['dhw'].values[0]

            # print('thw ', thw_ego)

            # # clip ttc to 0 - 200
            # ttc_ego = np.clip(ttc_ego, 0, 200)
            # # clip thw to 0 - 10
            # thw_ego = np.clip(thw_ego, 0, 10)
            # # clip dhw to 0 - 300
            # dhw_ego = np.clip(dhw_ego, 0, 300)

            # print('relative ditance ', relative_distance)

            plot_dict['frame'].append(frame)
            plot_dict['ego_speed'].append(ego_speed)
            plot_dict['preceding_speed'].append(preceding_speed)
            plot_dict['relative_speed'].append(relative_speed)
            plot_dict['relative_distance'].append(relative_distance)
            plot_dict['ttc_ego'].append(1/ttc_ego)
            plot_dict['thw_ego'].append(thw_ego)
            plot_dict['dhw_ego'].append(dhw_ego)

        plot_df = pd.DataFrame(plot_dict)
        # plot_df['ego_speed'] = (plot_df['ego_speed'] - plot_df['ego_speed'].min()) / (plot_df['ego_speed'].max() - plot_df['ego_speed'].min())
        # plot_df['preceding_speed'] = (plot_df['preceding_speed'] - plot_df['preceding_speed'].min()) / (plot_df['preceding_speed'].max() - plot_df['preceding_speed'].min())
        # plot_df['relative_speed'] = (plot_df['relative_speed'] - plot_df['relative_speed'].min()) / (plot_df['relative_speed'].max() - plot_df['relative_speed'].min())
        # # plot_df['relative_distance'] = (plot_df['relative_distance'] - plot_df['relative_distance'].min()) / (plot_df['relative_distance'].max() - plot_df['relative_distance'].min())
        # plot_df['ttc_ego'] = (plot_df['ttc_ego'] - plot_df['ttc_ego'].min()) / (plot_df['ttc_ego'].max() - plot_df['ttc_ego'].min())
        # plot_df['thw_ego'] = (plot_df['thw_ego'] - plot_df['thw_ego'].min()) / (plot_df['thw_ego'].max() - plot_df['thw_ego'].min())
        # plot_df['dhw_ego'] = (plot_df['dhw_ego'] - plot_df['dhw_ego'].min()) / (plot_df['dhw_ego'].max() - plot_df['dhw_ego'].min())
        # relative distance = dhw_ego when we scale with min and max
        # relative speed = ttc ego vehicle when we scale with min and max
    
        plot_df.plot(x='frame', y=['ego_speed',  'preceding_speed'], title=title)
        plot_df.plot(x='frame', y=['relative_speed'], title=title)
        plot_df.plot(x='frame', y=['relative_distance', 'dhw_ego'], title=title)
        plot_df.plot(x='frame', y=['ttc_ego', 'thw_ego'], title=title)
        pass

    

    def nFrames_vehicle_follow(self, follow_meta):
        df = follow_meta.copy(deep=True)
        df['nFrames'] = df['end_frame'] - df['start_frame']
        return np.sum(df['nFrames'].values)

    def follow_distance_distribution(self, follow_meta):
        tracks = self.data_container.tracks
        distance = []
        # print("follow meta ", follow_meta.columns, len(follow_meta))
        # print("tracks ", tracks.columns, len(tracks))
        for index, row in follow_meta.iterrows():
            ego_id = row['ego_id']
            preceding_id = row['preceding_id']
            start_frame = row['start_frame']
            end_frame = row['end_frame']

            ego_track = tracks[tracks['id'] == ego_id]
            ego_track = ego_track[ego_track['frame'].between(start_frame, end_frame)]
            ego_x, ego_y = ego_track['x'].values, ego_track['y'].values
            
            preceding_track = tracks[tracks['id'] == preceding_id]
            preceding_track = preceding_track[preceding_track['frame'].between(start_frame, end_frame)]
            preceding_x, preceding_y = preceding_track['x'].values, preceding_track['y'].values

            temp_distance = np.sqrt((ego_x - preceding_x)**2 + (ego_y - preceding_y)**2)
            distance.extend(temp_distance)

        df = pd.DataFrame(distance, columns=['followDistance'])
        df = df[df['followDistance'] < 50]
        print("df ", df.columns, len(df))
        Histogram.plotMetricsDF(df, 'followDistance', xlabel='Follow Distance (m)', bins=10, kde=True)
        pass

    def follow_relative_speed_distribution(self, follow_meta):
        tracks = self.data_container.tracks
        relative_speed = []
        for index, row in follow_meta.iterrows():
            ego_id = row['ego_id']
            preceding_id = row['preceding_id']
            start_frame = row['start_frame']
            end_frame = row['end_frame']

            ego_track = tracks[tracks['id'] == ego_id]
            ego_track = ego_track[ego_track['frame'].between(start_frame, end_frame)]
            ego_speed = ego_track['xVelocity'].values
            
            preceding_track = tracks[tracks['id'] == preceding_id]
            preceding_track = preceding_track[preceding_track['frame'].between(start_frame, end_frame)]
            preceding_speed = preceding_track['xVelocity'].values

            del_speed = ego_speed - preceding_speed
            relative_speed.extend(del_speed)

        df = pd.DataFrame(relative_speed, columns=['RelativeSpeed'])
        Histogram.plotMetricsDF(df, 'RelativeSpeed', xlabel='Relative Speed', bins=1000, kde=True)

    def follow_speed_distance_ratio(self, follow_meta):

        tracks = self.data_container.tracks
        distance = []
        relative_speed = []
        ratio = []

        for index, row in follow_meta.iterrows():
            ego_id = row['ego_id']
            preceding_id = row['preceding_id']
            start_frame = row['start_frame']
            end_frame = row['end_frame']

            ego_track = tracks[tracks['id'] == ego_id]
            ego_track = ego_track[ego_track['frame'].between(start_frame, end_frame)]

            ego_x, ego_y = ego_track['x'].values, ego_track['y'].values
            ego_speed = ego_track['xVelocity'].values
            
            preceding_track = tracks[tracks['id'] == preceding_id]
            preceding_track = preceding_track[preceding_track['frame'].between(start_frame, end_frame)]

            preceding_x, preceding_y = preceding_track['x'].values, preceding_track['y'].values
            preceding_speed = preceding_track['xVelocity'].values

            temp_distance = np.sqrt((ego_x - preceding_x)**2 + (ego_y - preceding_y)**2)
            distance.extend(temp_distance)

            del_speed = ego_speed - preceding_speed
            relative_speed.extend(del_speed)

            temp_ratio = abs(del_speed) / temp_distance

            ratio.extend(temp_ratio)
            # print('index = ', index)
            # break
        # df = pd.DataFrame(ratio, columns=['SpeedDistanceRatio'])
        df = pd.DataFrame({'distance': distance, 'relative_speed': relative_speed, 'ratio': ratio})

        Histogram.plotXY(df, 'distance', 'relative_speed', xlabel='Distance (m)', ylabel='Relative Speed (m/s)')
        pass
    



    def min_velocity_distribution(self):
        tracksMeta = self.data_container.tracksMeta.copy()
        tracksMeta['minXVelocity'] = tracksMeta['minXVelocity'] * 3.6
        Histogram.plotMetricsDF(tracksMeta, 'minXVelocity', xlabel='Min Velocity (km/h)', bins=100, kde=True)
        pass

    def max_velocity_distribution(self):
        tracksMeta = self.data_container.tracksMeta.copy()
        tracksMeta['maxXVelocity'] = tracksMeta['maxXVelocity'] * 3.6
        Histogram.plotMetricsDF(tracksMeta, 'maxXVelocity', xlabel='Max Velocity (km/h)', bins=100, kde=True)
        pass

    def mean_velocity_distribution(self):
        tracksMeta = self.data_container.tracksMeta.copy()
        tracksMeta['meanXVelocity'] = tracksMeta['meanXVelocity'] * 3.6
        Histogram.plotMetricsDF(tracksMeta, 'meanXVelocity', xlabel='Mean Velocity (km/h)', bins=100, kde=True)
        pass

    def min_distance_headway(self):
        tracksMeta = self.data_container.tracksMeta.copy()
        Histogram.plotMetricsDF(tracksMeta, 'minDHW', xlabel='Min Distance Headway (m)', bins=100, kde=True)
        pass

    def min_time_headway(self):
        tracksMeta = self.data_container.tracksMeta.copy()
        tracksMeta = tracksMeta[tracksMeta['minTHW'] > 0]
        Histogram.plotMetricsDF(tracksMeta, 'minTHW', xlabel='Min Time Headway (s)', bins=100, kde=True)
        pass

    def min_ttc(self):
        tracksMeta = self.data_container.tracksMeta.copy()
        tracksMeta = tracksMeta[tracksMeta['minTTC'] > 0]
        tracksMeta = tracksMeta[tracksMeta['minTTC'] < 200]
        Histogram.plotMetricsDF(tracksMeta, 'minTTC', xlabel='Min TTC (s)', bins=100, kde=True)
        pass

    def min_acceleration(self):
        tracksMeta = self.data_container.tracksMeta.copy()
        tracks = self.data_container.tracks.copy()

        # group tracks by id
        grouped_tracks = tracks.groupby('id')
        

        Histogram.plotMetricsDF(tracksMeta, 'minXAcceleration', xlabel='Min Acceleration (m/s^2)', bins=100, kde=True)
        pass
 