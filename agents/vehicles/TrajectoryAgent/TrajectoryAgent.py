from math import sqrt
import carla 
import random
import time
import numpy as np
import pandas as pd
import queue


class TrajectoryAgent():
    def __init__(self, vehicle, pivot, agent_id):

        self.vehicle = vehicle
        self.pivot = pivot
        self.agent_id = agent_id
        
        self.vehicle.set_simulate_physics(False)

        pass

    def onEnd(self):
        self.vehicle.destroy()
        pass
    
    def run_step(self, transform):

        self.vehicle.set_transform(transform)
        pass

    









