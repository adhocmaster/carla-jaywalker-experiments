import math
import os
from turtle import distance
import pandas as pd
import numpy as np
from analysis.EpisodeParser import EpisodeParser

class EpisodeParserCogMod():

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        self.preComputeDistanceBetweenAgents()

        self.episodeDf = {}
        self.createEpisodeDF()

        # frame number are for the full simulation,
        # we need to subtract the frame number of the first scene 
        # to get the frame number of the episode
        self.editFrameNos()

        self.validEpisodeIDs = self.filterValidEpisodes()
        
        pass


    def getEpisodeNos(self):
        return self.df.episode.unique()

    def getEpisodeDF(self, episodeNo):
        if episodeNo not in self.episodeDf:
            self.episodeDf[episodeNo] = self.df[self.df.episode == episodeNo]
        return self.episodeDf[episodeNo]
    
    def preComputeDistanceBetweenAgents(self):
        distance = ((self.df['c_x'] - self.df['a_x']) ** 2 + (self.df['c_y'] - self.df['a_y']) ** 2) ** 0.5
        self.df['distance'] = distance
        pass

    def createEpisodeDF(self):
        episodeID = self.getEpisodeNos()
        for episode in episodeID:
            self.getEpisodeDF(episode)
        pass

    def editFrameNos(self):
        temp_episodeDf = {}
        for key, values in self.episodeDf.items():
            values.sort_values(by=['frame'], inplace=False)
            first_val = values['frame'].iloc[0]
            values['frame'] = values['frame'] - first_val
            temp_episodeDf[key] = values

        self.episodeDf = temp_episodeDf

    def isValidEpisode(self, id):
        episodeDf = self.getEpisodeDF(id)
        if 'ScenarioState.START' in episodeDf['scenario_state'].unique():
            return True
        else:
            return False


    def filterValidEpisodes(self):
        valid_episodes = []
        for key, value in self.episodeDf.items():
            valid_episodes.append(key)
            # print('key: ', key)
            # print('value: ', value)
            # if self.isValidEpisode(key):
            #     valid_episodes.append(key)
        return valid_episodes

    def getValidEpisodes(self):
        valid_episodeDf = []
        for episode in self.validEpisodeIDs:
            valid_episodeDf.append(self.validEpisodeIDs[episode])
        return valid_episodeDf
