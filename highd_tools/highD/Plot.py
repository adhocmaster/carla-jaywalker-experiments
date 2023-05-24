from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
import math
import pandas as pd

class Plot():
    # the plot class does not do any filtering, it just plots the data
    @staticmethod
    def plot_tMeta_distributions(tMeta, title):
        
        # Define the columns to plot
        columns_to_plot = ['minDHW', 'minTHW', 'minTTC', 'minXVelocity', 'maxXVelocity', 'meanXVelocity']
        
        # Set up the subplots
        img_len = len(columns_to_plot)
        fig, axes = plt.subplots(1, img_len, figsize=(18, 4), sharey=False)
        fig.suptitle(title, fontsize=16)

        # Plot the distributions
        for idx, column in enumerate(columns_to_plot):
            sns.histplot(tMeta[column], kde=True, ax=axes[idx])
            axes[idx].set_title(column)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()
        
    
    @staticmethod
    def plot_speed_distribution_by_lane(combined_df, title):
        df = combined_df.copy()
        df['speed'] = np.sqrt(df['xVelocity']**2 + df['yVelocity']**2)
        unique_lanes = df['laneId'].unique()
        left_lanes, right_lanes = sorted(lane for lane in unique_lanes if lane < 0), sorted(lane for lane in unique_lanes if lane > 0)
        n_plots = len(left_lanes) + len(right_lanes)

        fig, axes = plt.subplots(1, n_plots, figsize=(n_plots * 4, 6), sharey=True)
        fig.suptitle(title, fontsize=16)

        plot_idx = 0
        for idx, lanes in enumerate([left_lanes, right_lanes]):
            lane_type = "Left" if idx == 0 else "Right"
            for lane in lanes:
                lane_data = df[df['laneId'] == lane]
                sns.histplot(lane_data['speed'], kde=True, ax=axes[plot_idx], color='blue', alpha=0.6)
                axes[plot_idx].set_title(f"Lane {lane_type} lane_no {abs(lane)}")
                plot_idx += 1

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()

    
    @staticmethod
    def plot_tracks_distributions(tracks, *columns, title,  bins=50):
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

    @staticmethod
    def plot_grid(plots):
        """
        Plots a list of matplotlib plots in a 4-column grid.

        :param plots: List of matplotlib plots to be displayed
        """
        n_plots = len(plots)
        n_rows = math.ceil(n_plots / 4)

        fig, axs = plt.subplots(n_rows, 4, figsize=(20, 5 * n_rows))
        fig.tight_layout(pad=3.0)

        for i, ax in enumerate(axs.flatten()):
            if i < n_plots:
                ax.axis('off')
                ax.imshow(plots[i].get_array(), cmap=plots[i].get_cmap())
            else:
                fig.delaxes(ax)




    @staticmethod
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
        # ttc_prec, thw_prec, dhw_prec = preceding_tracks[['ttc', 'thw', 'dhw']].values.T

        # Calculate TTC, THW, and DHW for ego and preceding vehicles
        ttc_ego, thw_ego, dhw_ego = ego_tracks[['ttc', 'thw', 'dhw']].values.T
        # ttc_prec, thw_prec, dhw_prec = preceding_tracks[['ttc', 'thw', 'dhw']].values.T

        # Clip values between 0 and 200
        ttc_ego_clipped = np.clip(ttc_ego, cMin, cMax)
        thw_ego_clipped = np.clip(thw_ego, cMin, cMax)
        dhw_ego_clipped = np.clip(dhw_ego, cMin, cMax)

        # ttc_prec_clipped = np.clip(ttc_prec, cMin, cMax)
        # thw_prec_clipped = np.clip(thw_prec, cMin, cMax)
        # dhw_prec_clipped = np.clip(dhw_prec, cMin, cMax)

        # Normalize ego values
        ttc_ego_norm = ttc_ego_clipped / np.linalg.norm(ttc_ego_clipped)
        thw_ego_norm = thw_ego_clipped / np.linalg.norm(thw_ego_clipped)
        dhw_ego_norm = dhw_ego_clipped / np.linalg.norm(dhw_ego_clipped)
        ttc_ego_norm = ttc_ego_clipped 
        thw_ego_norm = thw_ego_clipped 
        dhw_ego_norm = dhw_ego_clipped 

        # Normalize preceding values
        # ttc_prec_norm = ttc_prec_clipped / np.linalg.norm(ttc_prec_clipped)
        # thw_prec_norm = thw_prec_clipped / np.linalg.norm(thw_prec_clipped)
        # dhw_prec_norm = dhw_prec_clipped / np.linalg.norm(dhw_prec_clipped)

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

        # Plotting TTC distribution
        ttc_ego_clipped = ttc_ego_clipped[ttc_ego_clipped != cMin]
        ttc_ego_clipped = ttc_ego_clipped[ttc_ego_clipped != cMax]
        axs[2, 1].hist(ttc_ego_clipped, bins=20, edgecolor='black')
        axs[2, 1].set_xlabel('TTC Values')
        axs[2, 1].set_ylabel('Frequency')
        axs[2, 1].set_title('Distribution of TTC for Ego Vehicle')
        
    @staticmethod
    def plot_all_exec_nums(dataframe):
        # Assuming df is your DataFrame
        df = dataframe.copy()
        # group by exec_num
        grouped = df.groupby('exec_num')

        fig, axs = plt.subplots(1, 6, figsize=(30, 5))  # Increase number of subplots to 6

        # iterate over each group
        for name, group in grouped:
            # change frame number for each group to start at 1
            group['frame'] = group['frame'] - group['frame'].min() + 1
            
            group = group[group['scenario_status'] != 'ScenarioState.PENDING']
            
            axs[0].plot(group['frame'], group['a_speed'], label=f'a_speed {name}')
            axs[0].plot(group['frame'], group['c_speed'], label=f'c_speed {name}')

            axs[1].plot(group['frame'], group['c_steer'], label=f'exec_num {name}')
            axs[2].plot(group['frame'], group['c_throttle'], label=f'exec_num {name}')
            axs[3].plot(group['frame'], group['c_brake'], label=f'exec_num {name}')

            # plot gaze_direction
            group['gaze_direction'].value_counts().plot(kind='bar', ax=axs[4], label=f'exec_num {name}')

            # plot perceived_c_x, perceived_c_y, a_x, a_y in the sixth plot
            axs[5].plot(group['frame'], group['perceived_c_x'], label=f'perceived_c_x {name}')
            axs[5].plot(group['frame'], group['perceived_c_y'], label=f'perceived_c_y {name}')
            axs[5].plot(group['frame'], group['a_x'], label=f'a_x {name}')
            axs[5].plot(group['frame'], group['a_y'], label=f'a_y {name}')

        # Set labels and titles
        axs[0].set_xlabel('Frame')
        axs[0].set_ylabel('Speed')
        axs[0].set_title('Cogmod Speed across all Executions')
        # axs[0].legend()

        axs[1].set_xlabel('Frame')
        axs[1].set_ylabel('Steer')
        axs[1].set_title('Cogmod Steer across all Executions')
        # axs[1].legend()

        axs[2].set_xlabel('Frame')
        axs[2].set_ylabel('Throttle')
        axs[2].set_title('Cogmod Throttle across all Executions')
        # axs[2].legend()

        axs[3].set_xlabel('Frame')
        axs[3].set_ylabel('Brake')
        axs[3].set_title('Cogmod Brake across all Executions')
        # axs[3].legend()

        axs[4].set_xlabel('Gaze Direction')
        axs[4].set_ylabel('Count')
        axs[4].set_title('Gaze Direction across all Executions')
        # axs[4].legend()

        # set labels and title for the new plot
        axs[5].set_xlabel('Frame')
        axs[5].set_ylabel('Values')
        axs[5].set_title('Perceived and Actual Values across all Executions')
        # axs[5].legend()

        plt.tight_layout()
        plt.show()


    @staticmethod
    def plot_individual_exec_nums(dataframe, only_running=False):
        # group by exec_num
        grouped = dataframe.groupby('exec_num')

        for name, group in grouped:
            fig, axs = plt.subplots(1, 4, figsize=(20, 6))

            # change frame number for each group to start at 1
            group['frame'] = group['frame'] - group['frame'].min() + 1
            
            if only_running:
                group = group[group['scenario_status'] == 'ScenarioState.RUNNING']
            # remove the first frame 
            # group = group.drop(group.index[:2])
            
            # Create a new DataFrame for calculations
            calc_df = pd.DataFrame()
            calc_df['frame'] = group['frame']
            calc_df['perceived_distance'] = np.sqrt((group['c_x'] - group['perceived_c_x'])**2 
                                                    + (group['c_y'] - group['perceived_c_y'])**2)
            calc_df['actual_distance'] = np.sqrt((group['c_x'] - group['a_x'])**2 
                                                + (group['c_y'] - group['a_y'])**2)

            # scatter plot perceived_distance and actual_distance
            # axs[0].plot(calc_df['frame'], calc_df['perceived_distance'], label='Perceived Distance')
            # axs[0].plot(calc_df['frame'], calc_df['actual_distance'], label='Actual Distance')
            axs[0].plot(group['frame'], group['perceived_c_speed'], label='Perceived Velocity')
            axs[0].plot(group['frame'], group['a_speed'], label='Actual Velocity')
            
            
            axs[0].set_xlabel('Frame')
            axs[0].set_ylabel('Distance')
            axs[0].set_title(f'Perceived and Actual Distances and speed for exec_num {name}')
            axs[0].legend()

            for index, row in group.iterrows():
                frame = row['frame']
                direction = row['gaze_direction']
                color = Gaze_Settings[direction]
                axs[1].plot([frame, frame], [0, 10], color=color, linewidth=2)
            axs[1].set_xlabel('Gaze Direction')
            axs[1].set_title('Gaze Direction across all Executions')
            
            axs[2].plot(group['frame'], group['a_speed'], label=f'a_speed {name}')
            axs[2].plot(group['frame'], group['c_speed'], label=f'c_speed {name}')
            # axs[2].plot(group['frame'], group['target_speed'], label=f'target_speed {name}')
            axs[2].set_xlabel('Frame')
            axs[2].set_ylabel('Speed')
            axs[2].set_title('Cogmod and Actor Speed across all Executions')
            axs[2].legend()
            
            axs[3].plot(group['frame'], group['c_throttle'], label=f'c throttle')
            axs[3].plot(group['frame'], group['c_brake'], label=f'c brake')
            axs[3].set_xlabel('Frame')
            axs[3].set_ylabel('throttle and brake')
            axs[3].set_title('Cogmod Throttle and Brake across all Executions')
            
            
            plt.tight_layout()
            plt.show()



Gaze_Settings = {
    'GazeDirection.CENTER': 'lightcoral',
    'GazeDirection.LEFT': 'lightgreen',
    'GazeDirection.RIGHT': 'lightblue',
    'GazeDirection.LEFTBLINDSPOT': 'lightgreen',
    'GazeDirection.RIGHTBLINDSPOT': 'lightblue',
    'GazeDirection.LEFTMIRROR': 'lightgreen',
    'GazeDirection.RIGHTMIRROR': 'lightblue',
    'GazeDirection.BACK':  'lightcyan',
}


