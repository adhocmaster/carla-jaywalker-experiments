import numpy as np
import pandas as pd
from .PlotHelper import Histogram
from .ManeuverFilter import *


class HighDStats():
    def __init__(self, DataContainer):
        self.data_container = DataContainer

    def plot_agent_following_scenario(self, follow_meta):
        # Get the tracks dataframe from the data container
        tracks = self.data_container.tracks

        # Extract information about the scenario from the follow_meta dataframe
        ego_id = follow_meta['ego_id']
        preceding_id = follow_meta['preceding_id']
        start_frame = follow_meta['start_frame']
        end_frame = follow_meta['end_frame']

        # Create a title for the plot based on the scenario information
        title = f"Scenario {ego_id} - {preceding_id} - {end_frame - start_frame}"

        ego_tracks = tracks.loc[(tracks['id'] == ego_id) & (tracks['frame'] >= start_frame) & (tracks['frame'] < end_frame)]
        preceding_tracks = tracks.loc[(tracks['id'] == preceding_id) & (tracks['frame'] >= start_frame) & (tracks['frame'] < end_frame)]

        # Calculate speeds and distances
        ego_speed = np.abs(ego_tracks['xVelocity'].values)
        preceding_speed = np.abs(preceding_tracks['xVelocity'].values)
        relative_speed = ego_speed - preceding_speed

        ego_xy = ego_tracks[['x', 'y']].values
        preceding_xy = preceding_tracks[['x', 'y']].values
        relative_distance = np.sqrt(np.sum((ego_xy - preceding_xy)**2, axis=1))

        ttc_ego, thw_ego, dhw_ego = ego_tracks[['ttc', 'thw', 'dhw']].values.T

        # Create plot dataframe
        plot_df = pd.DataFrame({
            'frame': np.arange(start_frame, end_frame),
            'ego_speed': ego_speed,
            'preceding_speed': preceding_speed,
            'relative_speed': relative_speed,
            'relative_distance': relative_distance,
            'ttc_ego': 1 / ttc_ego,
            'thw_ego': thw_ego,
            'dhw_ego': dhw_ego,
        })

        # Create a 4-row grid for the plots
        fig, axs = plt.subplots(1, 4, figsize=(20, 5))

        # Create a subplot for each type of data to plot, and set the titles
        plot_df.plot(x='frame', y=['ego_speed', 'preceding_speed'], ax=axs[0], title=title)
        plot_df.plot(x='frame', y=['relative_speed'], ax=axs[1], title=title)
        plot_df.plot(x='frame', y=['relative_distance', 'dhw_ego'], ax=axs[2], title=title)
        plot_df.plot(x='frame', y=['ttc_ego', 'thw_ego'], ax=axs[3], title=title)

        # Adjust the spacing between the subplots
        plt.subplots_adjust(hspace=0.5)

        # Show the plot
        plt.show()




    def nFrames_vehicle_follow(self, follow_meta):
        df = follow_meta.copy(deep=True)
        df['nFrames'] = df['end_frame'] - df['start_frame']
        return np.sum(df['nFrames'].values)


    def follow_distance_distribution(self, follow_meta):
        tracks = self.data_container.tracks
        distance = []
        
        for _, row in follow_meta.iterrows():
            ego_id, preceding_id, start_frame, end_frame = row[['ego_id', 'preceding_id', 'start_frame', 'end_frame']]
            
            ego_track = tracks[(tracks['id'] == ego_id) & (tracks['frame'].between(start_frame, end_frame))]
            ego_x, ego_y = ego_track[['x', 'y']].values.T
            
            preceding_track = tracks[(tracks['id'] == preceding_id) & (tracks['frame'].between(start_frame, end_frame))]
            preceding_x, preceding_y = preceding_track[['x', 'y']].values.T
            
            temp_distance = np.sqrt((ego_x - preceding_x)**2 + (ego_y - preceding_y)**2)
            distance.extend(temp_distance)

        df = pd.DataFrame({'followDistance': distance})
        Histogram.plotMetricsDF(df, 'followDistance', xlabel='Follow Distance (m)', bins=10, kde=True)


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
        Histogram.plotMetricsDF(df, 'RelativeSpeed', xlabel='Relative Speed', bins=10, kde=True)

    import numpy as np

    def follow_speed_distance_ratio(self, follow_meta):
        # Get the tracks dataframe from the data container
        tracks = self.data_container.tracks

        # Initialize lists to hold the distance, relative speed, and ratio data
        distance, relative_speed, ratio = [], [], []

        # Loop through each follow scenario and extract relevant data
        for _, row in follow_meta.iterrows():
            ego_id, preceding_id, start_frame, end_frame = row[['ego_id', 'preceding_id', 'start_frame', 'end_frame']]

            ego_track = tracks[(tracks['id'] == ego_id) & (tracks['frame'].between(start_frame, end_frame))]
            ego_x, ego_y = ego_track[['x', 'y']].values.T
            ego_speed = ego_track['xVelocity'].values
            
            preceding_track = tracks[(tracks['id'] == preceding_id) & (tracks['frame'].between(start_frame, end_frame))]
            preceding_x, preceding_y = preceding_track[['x', 'y']].values.T
            preceding_speed = preceding_track['xVelocity'].values

            temp_distance = np.sqrt((ego_x - preceding_x)**2 + (ego_y - preceding_y)**2)
            distance.extend(temp_distance)

            del_speed = ego_speed - preceding_speed
            relative_speed.extend(del_speed)

            temp_ratio = abs(del_speed) / temp_distance
            ratio.extend(temp_ratio)

        # Create a dataframe from the extracted data
        df = pd.DataFrame({'distance': distance, 'relative_speed': relative_speed, 'ratio': ratio})

        # Plot the distance vs relative speed data
        Histogram.plotXY(df, 'distance', 'relative_speed', xlabel='Distance (m)', ylabel='Relative Speed (m/s)')


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
 