import os
import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Image
import seaborn as sns

def get_data_and_images(ids, DATA_DIRECTORY):
    # Set the root folder for the dataset
    project_folder = DATA_DIRECTORY
    
    # Create empty lists to store data frames and images
    dfs = []
    images = []
    
    # Loop through the ids
    for i in ids:
        # Read the CSV files and create a merged dataframe
        filename_recordingMeta = os.path.join(project_folder, f"{i}_recordingMeta.csv")
        filename_tracksMeta = os.path.join(project_folder, f"{i}_tracksMeta.csv")
        filename_tracks = os.path.join(project_folder, f"{i}_tracks.csv")

        df1 = pd.read_csv(filename_recordingMeta)
        df2 = pd.read_csv(filename_tracksMeta)
        df3 = pd.read_csv(filename_tracks)

        print(f'length df1, df2, df3 {len(df1)}, {len(df2)}, {len(df3)}')

        # append the dataframe as a tuple
        dfs.append((df1, df2, df3))
        # Read the image from the file 
        filename_image = os.path.join(project_folder, f"{i}_highway.PNG") # 01_highway.PNG
        image = cv2.imread(filename_image)
        images.append(image)
        
    return dfs, images




def filter_by_ttc(tracks, tMeta, ego_type, preceding_type, thw_lower_bound=0, thw_upper_bound=6, min_duration=-1, distance_threshold=100):
    car_following_meta = {'ego_id': [], 'preceding_id': [], 'start_frame': [], 'end_frame': []}

    all_ego_agent_id = set(tMeta[tMeta['class'] == ego_type]['id'].tolist())
    all_preceding_agent_id = set(tMeta[tMeta['class'] == preceding_type]['id'].tolist())

    frame_threshold = 25 * min_duration if min_duration != -1 else 2

    for ego_id in all_ego_agent_id:
        all_frames_with_agent = tracks[tracks['id'] == ego_id]
        unique_preceding_agent_list = list((set(all_frames_with_agent['precedingId'].unique()) & all_preceding_agent_id) - {0})

        for preceding_id in unique_preceding_agent_list:
            vehicle_follow_frames = all_frames_with_agent[all_frames_with_agent['precedingId'] == preceding_id]
            min_thw, max_thw = vehicle_follow_frames['thw'].min(), vehicle_follow_frames['thw'].max()

            # Compute initial distance and velocity difference directly
            initial_frame = vehicle_follow_frames['frame'].iloc[0]
            ego_track = tracks[(tracks['id'] == ego_id) & (tracks['frame'] == initial_frame)].iloc[0]
            preceding_track = tracks[(tracks['id'] == preceding_id) & (tracks['frame'] == initial_frame)].iloc[0]
            distance = np.sqrt((ego_track['x'] - preceding_track['x']) ** 2 + (ego_track['y'] - preceding_track['y']) ** 2)
            del_v = np.sqrt(ego_track['xVelocity'] ** 2 + ego_track['yVelocity'] ** 2) - np.sqrt(preceding_track['xVelocity'] ** 2 + preceding_track['yVelocity'] ** 2)

            if thw_lower_bound < min_thw <= thw_upper_bound and len(vehicle_follow_frames) >= frame_threshold and distance >= distance_threshold:
                car_following_meta['ego_id'].append(ego_id)
                car_following_meta['preceding_id'].append(preceding_id)
                car_following_meta['start_frame'].append(initial_frame)
                car_following_meta['end_frame'].append(vehicle_follow_frames['frame'].iloc[-1])

    return car_following_meta



def display_animated_gif(gif_path):
    return Image(filename=gif_path, format='png')

def plot_agent_following_scenario(tracks, follow_meta, cMin, cMax):
    # Extract information about the scenario from the follow_meta dataframe
    ego_id = follow_meta['ego_id']
    preceding_id = follow_meta['preceding_id']
    start_frame = follow_meta['start_frame']
    end_frame = follow_meta['end_frame']

    # Create a title for the plot based on the scenario information
    title = f"Scenario ego {ego_id} - prec {preceding_id} - start frame {start_frame}, end frame {end_frame}"

    # Get the relevant tracks for the scenario
    ego_tracks = tracks.loc[(tracks['id'] == ego_id) & (tracks['frame'] >= start_frame) & (tracks['frame'] < end_frame)]
    preceding_tracks = tracks.loc[(tracks['id'] == preceding_id) & (tracks['frame'] >= start_frame) & (tracks['frame'] < end_frame)]

    # Calculate speeds and distances
    ego_speed = np.abs(ego_tracks['xVelocity'].values)
    preceding_speed = np.abs(preceding_tracks['xVelocity'].values)
    relative_speed = ego_speed - preceding_speed

    ego_xy = ego_tracks[['x', 'y']].values
    preceding_xy = preceding_tracks[['x', 'y']].values
    relative_distance = np.sqrt(np.sum((ego_xy - preceding_xy)**2, axis=1))

    # Get ego acceleration from DataFrame
    ego_acceleration = ego_tracks['xAcceleration'].values

    # Calculate TTC, THW, and DHW for ego and preceding vehicles
    ttc_ego, thw_ego, dhw_ego = ego_tracks[['ttc', 'thw', 'dhw']].values.T
    ttc_prec, thw_prec, dhw_prec = preceding_tracks[['ttc', 'thw', 'dhw']].values.T

    # Calculate TTC, THW, and DHW for ego and preceding vehicles
    ttc_ego, thw_ego, dhw_ego = ego_tracks[['ttc', 'thw', 'dhw']].values.T
    ttc_prec, thw_prec, dhw_prec = preceding_tracks[['ttc', 'thw', 'dhw']].values.T

    # Clip values between 0 and 200
    ttc_ego_clipped = np.clip(ttc_ego, cMin, cMax)
    thw_ego_clipped = np.clip(thw_ego, cMin, cMax)
    dhw_ego_clipped = np.clip(dhw_ego, cMin, cMax)

    ttc_prec_clipped = np.clip(ttc_prec, cMin, cMax)
    thw_prec_clipped = np.clip(thw_prec, cMin, cMax)
    dhw_prec_clipped = np.clip(dhw_prec, cMin, cMax)

    # Normalize ego values
    ttc_ego_norm = ttc_ego_clipped / np.linalg.norm(ttc_ego_clipped)
    thw_ego_norm = thw_ego_clipped / np.linalg.norm(thw_ego_clipped)
    dhw_ego_norm = dhw_ego_clipped / np.linalg.norm(dhw_ego_clipped)

    # Normalize preceding values
    ttc_prec_norm = ttc_prec_clipped / np.linalg.norm(ttc_prec_clipped)
    thw_prec_norm = thw_prec_clipped / np.linalg.norm(thw_prec_clipped)
    dhw_prec_norm = dhw_prec_clipped / np.linalg.norm(dhw_prec_clipped)

    # Create a single plot with six subplots
    fig, axs = plt.subplots(3, 2, figsize=(15, 15), sharex='col')
    fig.suptitle(title)

    # Plot each type of data in a separate subplot
    axs[0, 0].plot(ego_tracks['frame'], ego_speed, label='Ego Speed')
    axs[0, 0].plot(ego_tracks['frame'], preceding_speed, label='Preceding Speed')
    axs[0, 0].set_title('Ego and Preceding Speed')
    axs[0, 0].legend()

    axs[0, 1].plot(ego_tracks['frame'], ego_acceleration, label='Ego Acceleration')
    axs[0, 1].set_title('Ego Acceleration')
    axs[0, 1].legend()

    axs[1, 0].plot(ego_tracks['frame'], relative_speed, label='Relative Speed')
    axs[1, 0].set_title('Relative Speed')
    axs[1, 0].legend()

    axs[1, 1].plot(ego_tracks['frame'], relative_distance, label='Relative Distance')
    axs[1, 1].set_title('Relative Distance')
    axs[1, 1].legend()

    axs[2, 0].plot(ego_tracks['frame'], ttc_ego_norm, label='TTC')
    axs[2, 0].plot(ego_tracks['frame'], thw_ego_norm, label='THW')
    axs[2, 0].plot(ego_tracks['frame'], dhw_ego_norm, label='DHW')
    axs[2, 0].set_title('TTC, THW, and DHW for Ego')
    axs[2, 0].legend()

    axs[2, 1].plot(preceding_tracks['frame'], ttc_prec_norm, label='TTC')
    axs[2, 1].plot(preceding_tracks['frame'], thw_prec_norm, label='THW')
    axs[2, 1].plot(preceding_tracks['frame'], dhw_prec_norm, label='DHW')
    axs[2, 1].set_title('TTC, THW, and DHW for Preceding Vehicle')
    axs[2, 1].legend()













def plot_speed_distribution_by_lane_and_type(combined_tracks, vehicle_type, title):
    # Merge tracks and tMeta DataFrames
    
    # Calculate the speed using both xVelocity and yVelocity and convert to km/h
    combined_tracks['speed'] = np.sqrt(combined_tracks['xVelocity']**2 + combined_tracks['yVelocity']**2) * 3.6
    
    # Filter by vehicle types
    vehicle_df = combined_tracks[combined_tracks['class'] == vehicle_type]

    # Get unique laneIds
    unique_lanes = combined_tracks['laneId'].unique()
    
    # Separate left and right lanes based on the laneId sign
    left_lanes = sorted([lane for lane in unique_lanes if lane < 0])
    right_lanes = sorted([lane for lane in unique_lanes if lane > 0])
    
    # Calculate the number of plots
    nplots = len(left_lanes) + len(right_lanes)
    
    # Set up the subplots
    fig, axes = plt.subplots(1, nplots, figsize=(nplots * 4, 6), sharey=True)
    fig.suptitle(title, fontsize=16)

    # Plot left and right lane speed distributions for the specified vehicle type
    curImage = 0
    for lanes in [left_lanes, right_lanes]:
        for lane in lanes:
            lane_data = vehicle_df[vehicle_df['laneId'] == lane]
            sns.histplot(lane_data['speed'], kde=True, ax=axes[curImage], color='blue', alpha=0.6)
            lane_type = "Left" if lane < 0 else "Right"
            axes[curImage].set_title(f"{vehicle_type} {lane_type} Lane {abs(lane)}")
            curImage += 1

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()








def plot_tMeta_distributions(tMeta, vehicle_type, title):
    # Filter by vehicle type
    vehicle_df = tMeta[tMeta['class'] == vehicle_type]
    
    # Define the columns to plot
    columns_to_plot = ['minDHW', 'minTHW', 'minTTC', 'minXVelocity', 'maxXVelocity', 'meanXVelocity']
    
    # Set up the subplots
    img_len = len(columns_to_plot)
    fig, axes = plt.subplots(1, img_len, figsize=(18, 4), sharey=False)
    fig.suptitle(title, fontsize=16)

    # Plot the distributions
    for idx, column in enumerate(columns_to_plot):
        sns.histplot(vehicle_df[column], kde=True, ax=axes[idx])
        axes[idx].set_title(column)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()







def plot_tracks_distributions(tracks, title, *columns, bins=50):
    # Set up the subplots
    img_len = len(columns)
    fig, axes = plt.subplots(1, img_len, figsize=(18, 4), sharey=False)
    fig.suptitle(title, fontsize=16)

    # Plot the distributions
    for idx, column in enumerate(columns):
        valid_data = tracks[tracks[column] != 0][column].dropna()
        sns.histplot(valid_data, kde=True, ax=axes[idx], bins=bins)
        axes[idx].set_title(column)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()




def calculate_ttc(df):
    # Extract required information from the DataFrame
    x_lead = df['x'] - df['width']
    x_follow = df['x']
    lead_length = df['width']
    v_lead = df['precedingXVelocity']
    v_follow = df['xVelocity']

    # Calculate the numerator and denominator of the TTC formula
    numerator = x_lead - x_follow - lead_length
    denominator = v_follow - v_lead

    # Avoid division by zero by replacing zeros in the denominator with a small value
    denominator = np.where(denominator == 0, 1e-9, denominator)

    # Calculate TTC
    ttc = numerator / denominator

    return ttc





def visualize_summary_statistics(tMeta, vehicle_type):
    # Filter by vehicle type
    vehicle_df = tMeta[tMeta['class'] == vehicle_type]

    # Define the columns to analyze
    columns_to_analyze = ['minDHW', 'minTHW', 'minTTC', 'minXVelocity', 'maxXVelocity', 'meanXVelocity']

    # Set up the subplots
    nplots = len(columns_to_analyze)
    fig, axes = plt.subplots(2, nplots, figsize=(nplots * 4, 10))
    fig.suptitle(f"Summary Statistics for {vehicle_type}s", fontsize=16)

    # Plot box plots and histograms for each column
    for i, col in enumerate(columns_to_analyze):
        sns.boxplot(y=col, data=vehicle_df, ax=axes[0, i], color='royalblue')
        sns.histplot(vehicle_df[col], kde=True, ax=axes[1, i], color='royalblue', alpha=0.6)
        axes[1, i].set_xlabel(col)

    # Adjust layout
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()





def combine_data(dfs):
    combined_dfs = []
    for df_tuple in dfs:
        rMeta, tMeta, tracks = df_tuple # unpack tuple
        # Merge the tracks and tMeta dataframes on the 'id' column
        combined_df = tracks.merge(tMeta[['id', 'class', 'drivingDirection']], on='id')

        # Add 'locationId' and 'id' from rMeta dataframe as new columns in combined_df
        combined_df['locationId'] = rMeta.loc[0, 'locationId']
        combined_df['dataset_id'] = rMeta.loc[0, 'id']

        # Reorder columns in the combined_df
        combined_df = combined_df[['dataset_id', 'locationId', 
                                'frame', 'id', 'class', 'drivingDirection', 'laneId',
                                'x', 'y', 'width', 'height', 'xVelocity', 'yVelocity', 
                                'xAcceleration', 'yAcceleration', 'frontSightDistance', 'backSightDistance', 
                                'dhw', 'thw', 'ttc', 'precedingXVelocity', 'precedingId', 'followingId', 
                                'leftPrecedingId', 'leftAlongsideId', 'leftFollowingId', 
                                'rightPrecedingId', 'rightAlongsideId', 'rightFollowingId']]
        print("combined_df.shape", combined_df.shape)
        combined_dfs.append(combined_df)
    print("combined_df.columns", combined_df.columns)
    
    return combined_dfs