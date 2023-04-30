from .ScenarioSettings import scenarios


class CogModSettings():
    def __init__(self, scenarioID):
    
        self.name = "CogModSettings"
        self.scenarioID = scenarioID

        self.currentSetting = scenarios[self.scenarioID]
    pass
    
    def getMapName(self):
        return self.currentSetting["map"]

    def getCogModAgentSettings(self):
        cur_settings = self.currentSetting["cogmod_agent"]
        return cur_settings
    
    def getActorAgentSettings(self):
        return self.currentSetting["actor_agent"]

    def getTriggerDistance(self):
        return self.currentSetting["trigger_distance"]
    
    def getHighDPath(self):
        return self.currentSetting["high_d_path"]

    def getDatasetID(self):
        return self.currentSetting["dataset_id"]
    
    def getStableHeightPath(self):
        return self.currentSetting["stable_height_path"]
    
    def getLaneID(self):
        return self.currentSetting["lane_id"]
    
    def getPivot(self):
        return self.currentSetting["pivot"]

    def getCarFollowSettings(self):
        return self.currentSetting["car_follow_settings"]
    
    def getBaseDistance(self):
        return self.currentSetting["base_distance"]
    
