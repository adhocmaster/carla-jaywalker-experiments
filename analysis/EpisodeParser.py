import math
import os
from turtle import distance
import pandas as pd
import numpy as np

class EpisodeParser:

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        self.episodeDf = {}
        # self.initComputation()
        self.preComputeR1V1()
        pass

    
    def preComputeR1V1(self):
        epDf = self.df.groupby("episode")
        self.df['w_x_diff'] = epDf['w_y'].diff()
        self.df['w_y_diff'] = epDf['w_y'].diff()
        self.df['w_d'] = (self.df['w_x_diff'] ** 2 + self.df['w_y_diff'] ** 2) ** (0.5)

        if "distance" not in self.df:
            # TODO we need to do P2P distance.
            self.df["distance"] = ((self.df["w_x"] - self.df["v_x"]) ** 2 + (self.df["w_y"] - self.df["v_y"]) ** 2) ** 0.5
        


    def getEpisodeNos(self):
        return self.df.episode.unique()

    
    def getEpisodeDF(self, episodeNo):
        if episodeNo not in self.episodeDf:
            self.episodeDf[episodeNo] = self.df[self.df.episode == episodeNo]
        return self.episodeDf[episodeNo]

    def calculateP2Pdistance(self, episodeNo):
        episodeDf = self.getEpisodeDF(episodeNo)
        maxIndex = len(episodeDf) - 1

        for index, row in episodeDf.iterrows():
            if index < maxIndex:
                nextRow =  episodeDf.iloc[index+1]
                walkerDistance = math.sqrt((row['w_x'] - nextRow['w_x']) ** 2 + (row['w_y'] - nextRow['w_y']) ** 2)
            else:
                walkerDistance = 0
    
    def getDistanceCoveredByEpisode(self, episodeNo, dCol):
        return self.df.groupby("episode")[dCol].sum()

    

    def getPedestrianSourceDest(self, xCol, yCol):
        # right now we will return the start and endpoints having greatest distance across all the episodes.
        episodeNos = self.getEpisodeNos()

        maxSrc = None
        maxDest = None
        maxD = 0

        for ep in episodeNos:
            epDf = self.getEpisodeDF(ep)
            first = epDf.iloc[0]
            last = epDf.iloc[-1]
            src = (first[xCol], first[yCol])
            dest = (last[xCol], last[yCol])

            distance = Geometry.distance(src, dest)

            if distance > maxD:
                maxD = distance
                maxSrc = src
                maxDest = dest

        
        return maxSrc, maxDest



    
    
