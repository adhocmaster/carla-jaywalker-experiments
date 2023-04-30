


from enum import Enum
import os
import pandas as pd

from lib import LoggerFactory




class DataCollector():

    def __init__(self):

        self.data_dict = None
        self.logger = LoggerFactory.create("DataCollector")
        self.trajectory_DF = pd.DataFrame()
        self.initDataDict()

        
        self.actor_speed_threshold = 8
        self.cogmod_speed_threshold = 13

        self.scenario_threshold = 1.5

        self.logger.info("DataCollector initialized")


    

    

    def initDataDict(self):
        
        self.statDict = {
            "episode": [], "frame": [],

            "c_x": [], "c_y": [], "c_speed": [],
            "c_steer": [], "c_throttle": [], "c_brake": [],
            # "v_direction": [],

            "a_x": [], "a_y": [], "a_speed": [],
            "a_steer": [], "a_throttle": [], "a_brake": [],
            # "w_direction": []
        }

  
        
    
    def collectStats(self, world_snapshot, cogmod_agent, actor_agent, episode):
        
        self.statDict["episode"].append(episode)
        self.statDict["frame"].append(world_snapshot.frame)

        self.statDict["c_x"].append(cogmod_agent.get_vehicle().get_location().x)
        self.statDict["c_y"].append(cogmod_agent.get_vehicle().get_location().y)
        self.statDict["c_speed"].append(cogmod_agent.get_vehicle().get_velocity().length())
        self.statDict["c_steer"].append(cogmod_agent.get_vehicle().get_control().steer)
        self.statDict["c_throttle"].append(cogmod_agent.get_vehicle().get_control().throttle)
        self.statDict["c_brake"].append(cogmod_agent.get_vehicle().get_control().brake)

        self.statDict["a_x"].append(actor_agent.get_vehicle().get_location().x)
        self.statDict["a_y"].append(actor_agent.get_vehicle().get_location().y)
        self.statDict["a_speed"].append(actor_agent.get_vehicle().get_velocity().length())
        self.statDict["a_steer"].append(actor_agent.get_vehicle().get_control().steer)
        self.statDict["a_throttle"].append(actor_agent.get_vehicle().get_control().throttle)
        self.statDict["a_brake"].append(actor_agent.get_vehicle().get_control().brake)

        # print('printing statdict')
        # print(self.statDict)
        pass
    
    def updateTrajectoryDF(self):
        # 1. make a dataframe from self.statDict
        df = pd.DataFrame.from_dict(self.statDict)
        # 2. merge it with the statDataframe
        # print(f'before merge {self.trajectory_DF.shape}')
        self.trajectory_DF = pd.concat([self.trajectory_DF, df], ignore_index=True)
        # print(f'after merge {self.trajectory_DF.shape}')
        # 3. clear self.statDict
        self.initDataDict()

    
    def saveCSV(self, filename, filepath):
        filepath = os.path.join(os.getcwd(), filepath, filename)
        print("filepath", filepath)
        self.logger.info(f"Saving CSV file to {filepath + '.csv'}")
        self.trajectory_DF.to_csv(filepath + ".csv", index=False)
        pass

    


    



