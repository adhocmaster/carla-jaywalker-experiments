


from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd


class VisualizationHelper(object):

    @staticmethod
    def plot_min_distance_together(episode_parsers, labels=None):
        id = 0
        df = pd.DataFrame()
        for episode_parser in episode_parsers:
            id += 1
            x = []
            y = []
            for key in episode_parser.validEpisodeIDs:
                dataframe = episode_parser.episodeDf[key]
                min_distance = dataframe['distance'].min()
                x.append(key)
                y.append(min_distance)
                pass
            df_dict = {'episode': id, 'distance': y}
            df_temp = pd.DataFrame.from_dict(df_dict)
            df = df.append(df_temp)

            # print(df.size)
            
        print(df.size)
        g = sns.FacetGrid(df, hue="episode", height=6, aspect=1.5)
        g = g.map(sns.distplot, "distance",  hist=False, rug=True)
        if labels is not None:
            plt.legend(labels=labels)
        plt.show()


    # @staticmethod
    # def box_plot(episode_parsers, labels):
    #     df = pd.DataFrame()
    #     for i in range(len(episode_parsers)):
    #         episode_parser = episode_parsers[i]
    #         label = labels[i]
    #         x = []
    #         y = []
    #         for key in episode_parser.validEpisodeIDs:
    #             dataframe = episode_parser.episodeDf[key]
    #             min_distance = dataframe['distance'].min()
    #             x.append(key)
    #             y.append(min_distance)
    #             pass
    #         df_dict = {'server': label, 'distance': y}
    #         df_temp = pd.DataFrame.from_dict(df_dict)
    #         df = df.append(df_temp)
    #         # print(df.size) 
        
    #     print(df.size)
    #     sns.boxplot(x="server", y="distance", data=df)
    #     pass