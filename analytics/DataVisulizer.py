
import pandas as pd
from analysis.Histogram import Histogram
import seaborn as sns
import matplotlib.pyplot as plt


class DataVisualizer(object):

    def __init__(self, episode_parser):
        self.episodeParser = episode_parser
        pass
    
    def print_meta_info(self):
        print(f' total number of episode {len(self.episodeParser.getEpisodeNos())}')
        pass


    # plotting the minimum distance for each episode
    def plot_min_distance_histogram(self):
        x = []
        y = []
        for key in self.episodeParser.validEpisodeIDs:
            dataframe = self.episodeParser.episodeDf[key]
            min_distance = dataframe['distance'].min()
            x.append(key)
            y.append(min_distance)
            pass
        df_dict = {'episode': x, 'distance': y}
        df = pd.DataFrame.from_dict(df_dict)
        Histogram.plotMetricsDF(df, 'distance', 'minimum distance', bins=10)
        pass
    
    # plotting velocity distribution of all episodes
    def plot_velocity_distribution(self):
        speed = []
        episode_list = []
        for episode in self.episodeParser.validEpisodeIDs:
            episode = self.episodeParser.episodeDf[episode]
            episode_list += episode['episode'].tolist()
            speed += episode['c_speed'].tolist()

        df_dict = {'episode': episode_list, 'speed': speed}
        df = pd.DataFrame.from_dict(df_dict)

        Histogram.plotMetricsDF(df, 'speed', bins=100)
    
    




