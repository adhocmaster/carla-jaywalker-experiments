import os
import cv2
import pandas as pd


class HighD:
    def __init__(self, ids, data_directory):
        self.ids = ids
        self.data_directory = data_directory
        self.dfs, self.images = self._load_data_and_images()
        self.combined_dfs = self._combine_dataframes()

    def _load_data_and_images(self):
        dfs = []
        images = []

        for i in self.ids:
            dfs.append(self._load_dataframes(i))
            images.append(self._load_image(i))
            print(f"Loaded data and image for dataset {i}.")

        return dfs, images

    def _load_dataframes(self, i):
        def read_csv(filename):
            return pd.read_csv(os.path.join(self.data_directory, f"{i}_{filename}.csv"))

        return read_csv("recordingMeta"), read_csv("tracksMeta"), read_csv("tracks")

    def _load_image(self, i):
        return cv2.imread(os.path.join(self.data_directory, f"{i}_highway.PNG"))

    def _combine_dataframes(self):
        combined_dfs = []

        for r_meta, t_meta, tracks in self.dfs:
            combined_df = tracks.merge(t_meta[['id', 'class', 'drivingDirection']], on='id')
            combined_df['locationId'] = r_meta.loc[0, 'locationId']
            combined_df['dataset_id'] = r_meta.loc[0, 'id']
            combined_df = combined_df[[
                'dataset_id', 'locationId', 'frame', 'id', 'class', 'drivingDirection', 'laneId',
                'x', 'y', 'width', 'height', 'xVelocity', 'yVelocity', 'xAcceleration', 'yAcceleration',
                'frontSightDistance', 'backSightDistance', 'dhw', 'thw', 'ttc', 'precedingXVelocity',
                'precedingId', 'followingId', 'leftPrecedingId', 'leftAlongsideId', 'leftFollowingId',
                'rightPrecedingId', 'rightAlongsideId', 'rightFollowingId'
            ]]
            combined_dfs.append(combined_df)

        return combined_dfs

    def get_dataframe_tuple(self, id):
        return self.dfs[id-1]

    def get_image(self, id):
        return self.images[id-1]

    def get_combined_dataframe(self, id):
        return self.combined_dfs[id-1]

    def get_images(self):
        return self.images

    def get_combined_dataframes(self):
        return self.combined_dfs
