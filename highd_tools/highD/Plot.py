from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns

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

    # @staticmethod
    # def visualize_summary_statistics(tMeta, vehicle_type):
    #     # Filter by vehicle type
    #     vehicle_df = tMeta[tMeta['class'] == vehicle_type]

    #     # Define the columns to analyze
    #     columns_to_analyze = ['minDHW', 'minTHW', 'minTTC', 'minXVelocity', 'maxXVelocity', 'meanXVelocity']

    #     # Set up the subplots
    #     nplots = len(columns_to_analyze)
    #     fig, axes = plt.subplots(2, nplots, figsize=(nplots * 4, 10))
    #     fig.suptitle(f"Summary Statistics for {vehicle_type}s", fontsize=16)

    #     # Plot box plots and histograms for each column
    #     for i, col in enumerate(columns_to_analyze):
    #         sns.boxplot(y=col, data=vehicle_df, ax=axes[0, i], color='royalblue')
    #         sns.histplot(vehicle_df[col], kde=True, ax=axes[1, i], color='royalblue', alpha=0.6)
    #         axes[1, i].set_xlabel(col)

    #     # Adjust layout
    #     plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    #     plt.show()




    # @staticmethod
    # def plot_agent_following_scenario(tracks, follow_meta, cMin, cMax):
    #     # Extract information about the scenario from the follow_meta dataframe
    #     ego_id = follow_meta['ego_id']
    #     preceding_id = follow_meta['preceding_id']
    #     start_frame = follow_meta['start_frame']
    #     end_frame = follow_meta['end_frame']

    #     # Create a title for the plot based on the scenario information
    #     title = f"Scenario ego {ego_id} - prec {preceding_id} - start frame {start_frame}, end frame {end_frame}"

    #     # Get the relevant tracks for the scenario
    #     ego_tracks = tracks.loc[(tracks['id'] == ego_id) & (tracks['frame'] >= start_frame) & (tracks['frame'] < end_frame)]
    #     preceding_tracks = tracks.loc[(tracks['id'] == preceding_id) & (tracks['frame'] >= start_frame) & (tracks['frame'] < end_frame)]

    #     # Calculate speeds and distances
    #     ego_speed = np.abs(ego_tracks['xVelocity'].values)
    #     preceding_speed = np.abs(preceding_tracks['xVelocity'].values)
    #     relative_speed = ego_speed - preceding_speed

    #     ego_xy = ego_tracks[['x', 'y']].values
    #     preceding_xy = preceding_tracks[['x', 'y']].values
    #     relative_distance = np.sqrt(np.sum((ego_xy - preceding_xy)**2, axis=1))

    #     # Get ego acceleration from DataFrame
    #     ego_acceleration = ego_tracks['xAcceleration'].values

    #     # Calculate TTC, THW, and DHW for ego and preceding vehicles
    #     ttc_ego, thw_ego, dhw_ego = ego_tracks[['ttc', 'thw', 'dhw']].values.T
    #     ttc_prec, thw_prec, dhw_prec = preceding_tracks[['ttc', 'thw', 'dhw']].values.T

    #     # Calculate TTC, THW, and DHW for ego and preceding vehicles
    #     ttc_ego, thw_ego, dhw_ego = ego_tracks[['ttc', 'thw', 'dhw']].values.T
    #     ttc_prec, thw_prec, dhw_prec = preceding_tracks[['ttc', 'thw', 'dhw']].values.T

    #     # Clip values between 0 and 200
    #     ttc_ego_clipped = np.clip(ttc_ego, cMin, cMax)
    #     thw_ego_clipped = np.clip(thw_ego, cMin, cMax)
    #     dhw_ego_clipped = np.clip(dhw_ego, cMin, cMax)

    #     ttc_prec_clipped = np.clip(ttc_prec, cMin, cMax)
    #     thw_prec_clipped = np.clip(thw_prec, cMin, cMax)
    #     dhw_prec_clipped = np.clip(dhw_prec, cMin, cMax)

    #     # Normalize ego values
    #     ttc_ego_norm = ttc_ego_clipped / np.linalg.norm(ttc_ego_clipped)
    #     thw_ego_norm = thw_ego_clipped / np.linalg.norm(thw_ego_clipped)
    #     dhw_ego_norm = dhw_ego_clipped / np.linalg.norm(dhw_ego_clipped)

    #     # Normalize preceding values
    #     ttc_prec_norm = ttc_prec_clipped / np.linalg.norm(ttc_prec_clipped)
    #     thw_prec_norm = thw_prec_clipped / np.linalg.norm(thw_prec_clipped)
    #     dhw_prec_norm = dhw_prec_clipped / np.linalg.norm(dhw_prec_clipped)

    #     # Create a single plot with six subplots
    #     fig, axs = plt.subplots(3, 2, figsize=(15, 15), sharex='col')
    #     fig.suptitle(title)

    #     # Plot each type of data in a separate subplot
    #     axs[0, 0].plot(ego_tracks['frame'], ego_speed, label='Ego Speed')
    #     axs[0, 0].plot(ego_tracks['frame'], preceding_speed, label='Preceding Speed')
    #     axs[0, 0].set_title('Ego and Preceding Speed')
    #     axs[0, 0].legend()

    #     axs[0, 1].plot(ego_tracks['frame'], ego_acceleration, label='Ego Acceleration')
    #     axs[0, 1].set_title('Ego Acceleration')
    #     axs[0, 1].legend()

    #     axs[1, 0].plot(ego_tracks['frame'], relative_speed, label='Relative Speed')
    #     axs[1, 0].set_title('Relative Speed')
    #     axs[1, 0].legend()

    #     axs[1, 1].plot(ego_tracks['frame'], relative_distance, label='Relative Distance')
    #     axs[1, 1].set_title('Relative Distance')
    #     axs[1, 1].legend()

    #     axs[2, 0].plot(ego_tracks['frame'], ttc_ego_norm, label='TTC')
    #     axs[2, 0].plot(ego_tracks['frame'], thw_ego_norm, label='THW')
    #     axs[2, 0].plot(ego_tracks['frame'], dhw_ego_norm, label='DHW')
    #     axs[2, 0].set_title('TTC, THW, and DHW for Ego')
    #     axs[2, 0].legend()

    #     axs[2, 1].plot(preceding_tracks['frame'], ttc_prec_norm, label='TTC')
    #     axs[2, 1].plot(preceding_tracks['frame'], thw_prec_norm, label='THW')
    #     axs[2, 1].plot(preceding_tracks['frame'], dhw_prec_norm, label='DHW')
    #     axs[2, 1].set_title('TTC, THW, and DHW for Preceding Vehicle')
    #     axs[2, 1].legend()



