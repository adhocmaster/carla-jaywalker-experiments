import math
import carla 
import logging
from lib import SimulationMode, Simulator
from research.BaseCogModResearch import BaseCogModResearch
from settings.CogModSettings import CogModSettings
from agents.vehicles.TrajectoryAgent.helper import HighD_Processor
import pandas as pd

from agents.vehicles.TrajectoryAgent import TrajectoryAgent


class ResearchTrajectory(BaseCogModResearch):

    def __init__(self, 
                 client, 
                 logLevel=logging.INFO, 
                 outputDir="logs", 
                 simulationMode=SimulationMode.SYNCHRONOUS, 
                 scenarioID="scenario3"):



        self.name = "research trajectory"
        self.scenarioID = scenarioID
        self.researchSettings = CogModSettings(scenarioID)

        self.mapName = self.researchSettings.getMapName()
        self.highDPath = self.researchSettings.getHighDPath()
        self.stableHeightPath = self.researchSettings.getStableHeightPath()
        self.laneID = self.researchSettings.getLaneID()
        self.pivot = self.researchSettings.getPivot()
        
        
        if simulationMode != SimulationMode.SYNCHRONOUS:
            raise Exception("research trajectory only supports synchronous mode")
            exit(1)

        super().__init__(name=self.name, 
                         client=client, 
                         mapName=self.mapName, 
                         logLevel=logLevel, 
                         outputDir=outputDir, 
                         simulationMode=simulationMode, 
                         showSpawnPoints=True)

        # self.agent = None
        self.agent_list = {}

        self.tracks = HighD_Processor.read_highD_data(self.highDPath)
        self.stable_height_dict = HighD_Processor.read_stable_height_dict(self.stableHeightPath)

        self.left_lane_id = set(self.laneID['left_lane'])
        self.right_lane_id = set(self.laneID['right_lane'])
        
        self.logger.info(f"research trajectory initialized")
        pass


    def run(self, maxTicks=100):

        self.SetSpectator(location=carla.Location(180, -5), height=50)

        onTickers = [self.onTick]
        onEnders = [self.onEnd]

        self.simulator = Simulator(self.client, onTickers=onTickers, onEnders=onEnders, simulationMode=self.simulationMode)
        self.simulator.run(maxTicks=maxTicks)

        pass

    def onTick(self, tick):

        frame_id = tick
        frameDF = self.tracks[self.tracks["frame"] == frame_id]
        
        actor_id_cur_frame = list(frameDF["id"])
        actor_id_prev_frame = list(self.agent_list.keys())

        create_actor_with_id = list(set(actor_id_cur_frame) - set(actor_id_prev_frame))
        update_actor_with_id = list(set(actor_id_cur_frame) & set(actor_id_prev_frame))
        remove_actor_with_id = list(set(actor_id_prev_frame) - set(actor_id_cur_frame))
        
        for id in create_actor_with_id:
            row = frameDF[frameDF["id"] == id]
            location, rotation = self.get_vehicle_transform(row, 0.5)
            self.createTrajectoryAgent(id, self.tracks, self.pivot, 0.5)
        
        for id in update_actor_with_id:
            row = frameDF[frameDF["id"] == id]
            agent = self.agent_list[id]
            
            vehicle_type = agent.vehicle.type_id
            stable_height = self.stable_height_dict[vehicle_type]

            location, rotation = self.get_vehicle_transform(row, stable_height)
            cur_destination_transform = carla.Transform(location, rotation)

            mVel, aVel = self.velocity_tracker(row)
            
            self.visualizer.drawTextOnMap(location=carla.Location(x=location.x+2, y=location.y, z=location.z),
                                          text=f"mVel: {mVel:.2f} m/s",
                                          color=(0,0,255),
                                          life_time=0.05)
            self.visualizer.drawTextOnMap(location=location,
                                          text=f"aVel: {aVel:.2f} m/s",
                                          color=(255,0,0),
                                          life_time=0.05)
            
            agent.run_step(cur_destination_transform)
        
        for id in remove_actor_with_id:
            # call onEnd for agent in agent list
            agent = self.agent_list[id]
            agent.onEnd()
            del self.agent_list[id]

        pass

    def get_vehicle_transform(self, row, height):

        center_x, center_y = self.transform_coordinate_wrt_pivot(row)
        location = carla.Location(x=center_x, y=center_y, z=height)
        laneID = int(row["laneId"])
        
        rotation = carla.Rotation(yaw=180)
        if laneID in self.left_lane_id:
            rotation = carla.Rotation(yaw=0)
        return location,rotation

    def transform_coordinate_wrt_pivot(self, row):
        x, y, width, height = row["x"], row["y"], row["width"], row["height"]
        center_x = x + width/2
        center_y = y + height/2
        center_x = center_x + self.pivot.location.x
        center_y = center_y + self.pivot.location.y
        return float(center_x), float(center_y)

    def velocity_tracker(self, row):
        aVelX = row["xVelocity"]
        aVelY = row["yVelocity"]
        aVel = math.sqrt(math.pow(aVelX, 2) + math.pow(aVelY, 2))
        
        prev_time_step = row["frame"].values[0] - 1
        id = row["id"].values[0]
        
        c_x = self.tracks[(self.tracks["frame"] == row["frame"].values[0]) & (self.tracks["id"] == id)]["x"].values[0]
        c_y = self.tracks[(self.tracks["frame"] == row["frame"].values[0]) & (self.tracks["id"] == id)]["y"].values[0]
        p_x = self.tracks[(self.tracks["frame"] == prev_time_step) & (self.tracks["id"] == id)]["x"].values[0]
        p_y = self.tracks[(self.tracks["frame"] == prev_time_step) & (self.tracks["id"] == id)]["y"].values[0]
        
        d = math.sqrt(math.pow(c_x - p_x, 2) + math.pow(c_y - p_y, 2))
        return d/0.04, aVel
    
    def onEnd(self):
        self.logger.info(f"research trajectory onEnd")
        for key, agent in self.agent_list.items():
            agent.onEnd()
        
        pass

    




