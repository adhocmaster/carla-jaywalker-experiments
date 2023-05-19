


from enum import Enum
import os
import pandas as pd

from lib import LoggerFactory




class DataCollectorCarFollowWithRepeat():

    def __init__(self):

        self.data_dict = None
        self.logger = LoggerFactory.create("DataCollector")
        self.trajectory_DF = pd.DataFrame()
        self.initDataDict()

        self.logger.info("DataCollector car follow initialized")


    def initDataDict(self):
        
        self.statDict = {
            "scenario_id": [], "exec_num": [], "frame": [], "scenario_status": [],

            "ego_id": [], "c_x": [], "c_y": [], 
            "c_speed": [], "c_acceleration": [], 
            "c_steer": [], "c_throttle": [], "c_brake": [],
            "perceived_c_x": [], "perceived_c_y": [], "perceived_c_speed": [],
            "gaze_direction": [],

            "preceding_id": [],
            "a_x": [], "a_y": [], "a_speed": [],
        }

  
        
    
    def collectStats(self, frame, ego_id, preceding_id, cogmod_agent, actor_agent, scenario_id, scenario_status, exec_num):
        
        self.statDict["scenario_id"].append(scenario_id)
        self.statDict["exec_num"].append(exec_num)
        self.statDict["frame"].append(frame)
        self.statDict["scenario_status"].append(scenario_status)

        self.statDict["ego_id"].append(ego_id)
        self.statDict["c_x"].append(cogmod_agent.get_vehicle().get_location().x)
        self.statDict["c_y"].append(cogmod_agent.get_vehicle().get_location().y)
        
        self.statDict["c_speed"].append(cogmod_agent.get_vehicle().get_velocity().length())
        self.statDict["c_acceleration"].append(cogmod_agent.get_vehicle().get_velocity().length())
        
        self.statDict["c_steer"].append(cogmod_agent.get_vehicle().get_control().steer)
        self.statDict["c_throttle"].append(cogmod_agent.get_vehicle().get_control().throttle)
        self.statDict["c_brake"].append(cogmod_agent.get_vehicle().get_control().brake)
        
        front_WM = cogmod_agent.local_map.trackedAgentManager.surrounding_agents['front']
        self.statDict["perceived_c_x"].append(front_WM.location_t_1.x)
        self.statDict["perceived_c_y"].append(front_WM.location_t_1.y)
        self.statDict["perceived_c_speed"].append(front_WM.velocity_t_1.length())

        self.statDict["gaze_direction"].append(cogmod_agent.gaze.get_gaze_direction())

        self.statDict["preceding_id"].append(preceding_id)
        self.statDict["a_x"].append(actor_agent.get_vehicle().get_location().x)
        self.statDict["a_y"].append(actor_agent.get_vehicle().get_location().y)
        self.statDict["a_speed"].append(actor_agent.get_velocity().length())

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

    


    



