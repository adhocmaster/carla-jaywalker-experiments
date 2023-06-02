
import carla
from datetime import datetime as date
import logging
from lib import SimulationMode, Simulator
from research.BaseCogModResearch import BaseCogModResearch
from settings.CogModSettings import CogModSettings
from agents.vehicles.TrajectoryAgent.helper import HighD_Processor
from analytics.DataCollectorCarFollowWithRepeat import DataCollectorCarFollowWithRepeat
from highd_tools.highD.HighD import HighD 
from highd_tools.highD.Filter import Filter
import pandas as pd
import numpy as np
from .ResearchCogMod import ScenarioState



class FilterCarFollow():
    def __init__(self, dataset_id):
        
        self.highDPath = f'D:\\highD_data\\highD_dataset'
        self.car_follow_settings = {
            "car_follow_settings":{
                        'ego_type': 'Car',
                        'preceding_type': 'Car',
                        'time_duration': 5,
                        'distance_threshold': 50,
                },
            }
        self.dataset_id = dataset_id
        self.highD = HighD([self.dataset_id], self.highDPath)
        self.df = self.highD.get_combined_dataframe(int(self.dataset_id))
        
        self.ego_type = self.car_follow_settings['ego_type']
        self.preceding_type = self.car_follow_settings['preceding_type']
        self.time_duration = self.car_follow_settings['time_duration']
        self.distance_threshold = self.car_follow_settings['distance_threshold']
        
        self.follow_meta = Filter.filter_vehicle_follow_scenario(self.df, 
                                                                 self.ego_type,
                                                                 self.preceding_type,
                                                                 self.time_duration,
                                                                 self.distance_threshold,
                                                                 100,
                                                                 removeStrictDistanceInc=True)
        
        # print(f'total extracted scenarios {len(self.follow_meta)}')
        
    def get_follow_meta(self):
        return self.follow_meta
    
    def get_combined_df(self):
        return self.df
    
    

class DriverModifier():

    @staticmethod
    def change_cogmod_settings_start_simulation(prev_cogmod_settings, ego_agent_df):
        cogmod_settings = prev_cogmod_settings
        velocity_df = np.sqrt(ego_agent_df['xVelocity']**2 + ego_agent_df['yVelocity']**2)

        positive_acceleration_df = ego_agent_df[ego_agent_df['xAcceleration'] >= 0]
        negative_acceleration_df = ego_agent_df[ego_agent_df['xAcceleration'] < 0]

        if not positive_acceleration_df.empty:
            max_acceleration = np.max(np.sqrt(positive_acceleration_df['xAcceleration']**2 + positive_acceleration_df['yAcceleration']**2))
        # else:
        #     max_acceleration = 1

        if not negative_acceleration_df.empty:
            comfort_deceleration = np.nanmean(np.sqrt(negative_acceleration_df['xAcceleration']**2 + negative_acceleration_df['yAcceleration']**2)) * 3.6**2
        else:
            comfort_deceleration = 1e-5

        desired_velocity = velocity_df.max()
        safe_time_headway = (1 / ego_agent_df[ego_agent_df['thw'] != 0]['thw'].min())

        
        subtasks_parameters = cogmod_settings['driver_profile']['subtasks_parameters']
        lane_following_subtask = subtasks_parameters['lane_following']

        lane_following_subtask['desired_velocity'] = desired_velocity
        lane_following_subtask['safe_time_headway'] = 1e-6
        lane_following_subtask['max_acceleration'] = 10
        lane_following_subtask['comfort_deceleration'] = 1.67
        lane_following_subtask['acceleration_exponent'] = 4
        lane_following_subtask['minimum_distance'] = 2
        lane_following_subtask['vehicle_length'] = 5
        

        subtasks_parameters['lane_following'] = lane_following_subtask
        cogmod_settings['driver_profile']['subtasks_parameters'] = subtasks_parameters
        print('cogmod settings after ', lane_following_subtask)
        return cogmod_settings

    @staticmethod
    def change_cogmod_settings_pending_simulation(preceding_agent, spawn_distance, tracking_distance, cogmod_settings, ego_agent_df):
        
        map = preceding_agent.vehicle.get_world().get_map()
        preceding_agent_location = preceding_agent.vehicle.get_location()
        nearest_waypoint_preceding_agent = map.get_waypoint(preceding_agent_location, project_to_road=True)
        velocity_df = np.sqrt(ego_agent_df['xVelocity']**2 + ego_agent_df['yVelocity']**2)
        desired_velocity = velocity_df.max()
        
        local_map = cogmod_settings['driver_profile']['local_map']
        local_map['vehicle_tracking_radius'] = tracking_distance
        
        spawn_waypoint = nearest_waypoint_preceding_agent.previous(spawn_distance)[0]
        spawn_transform = spawn_waypoint.transform
        spawn_location = spawn_transform.location
        spawn_location = carla.Vector3D(spawn_location.x, spawn_location.y, 1.0)

        destination_transform = preceding_agent.get_destination_transform()
        destination_waypoint = map.get_waypoint(destination_transform.location, project_to_road=True)
        destination_location = destination_waypoint.transform.location

        cogmod_settings['source'] = spawn_location
        cogmod_settings['destination'] = destination_location

        lane_following_subtask = cogmod_settings['driver_profile']['subtasks_parameters']['lane_following']
        lane_following_subtask['desired_velocity'] = desired_velocity
        lane_following_subtask['safe_time_headway'] = 0
        lane_following_subtask['max_acceleration'] = 20
        lane_following_subtask['comfort_deceleration'] = 0.5
        lane_following_subtask['acceleration_exponent'] = 5
        lane_following_subtask['minimum_distance'] = 2
        lane_following_subtask['vehicle_length'] = 4
        print('cogmod settings before ', lane_following_subtask)
        return cogmod_settings


class AgentViz():
    @classmethod
    def get_vehicle_transform(cls, row, center_x, center_y, height, left_lane_id):
        location = carla.Location(x=center_x, y=center_y, z=height)
        rotation = carla.Rotation(yaw=180)
        if int(row["laneId"]) in left_lane_id:
            rotation = carla.Rotation(yaw=0)
        return location, rotation
    
    @staticmethod
    def draw_ego(frame, tracks, agent_id, left_lane_id, debug, pivot, show_speed=False):
        row = tracks[(tracks['frame'] == frame) & (tracks['id'] == agent_id)].iloc[0]
        xVel, yVel = row[['xVelocity', 'yVelocity']]
        center_x, center_y = AgentViz.transform_coordinate_wrt_pivot(row, pivot)
        location, rotation = AgentViz.get_vehicle_transform(row, center_x, center_y, 0.5, left_lane_id)
        debug.draw_point(location, size=0.1, color=carla.Color(255, 0, 0), life_time=0.1)
        if show_speed:
            # print('ego speed in data ', round(np.sqrt(xVel**2 + yVel**2), 2))
            pass  # Do something with the speed
        
    @staticmethod
    def transform_coordinate_wrt_pivot(row, pivot):
        x, y, width, height = row[["x", "y", "width", "height"]]
        center_x = float(x + width/2 + pivot.location.x)
        center_y = float(y + height/2 + pivot.location.y)
        return center_x, center_y


def read_stable_height_dict(path):
    stable_height = pd.read_csv(path)
    stable_height_dict = {}
    for i in range(len(stable_height)):
        stable_height_dict[stable_height.iloc[i,0]] = stable_height.iloc[i,1]
    return stable_height_dict

def get_left_right_lanes(df):
    left_lanes = df[df['drivingDirection'] == 1]['laneId'].unique()
    right_lanes = df[df['drivingDirection'] == 2]['laneId'].unique()

    return left_lanes, right_lanes

class ResearchCarFollowRepeat(BaseCogModResearch):
    def __init__(self, 
                 client, 
                 logLevel=logging.INFO, 
                 outputDir="logs", 
                 simulationMode=SimulationMode.SYNCHRONOUS, 
                 scenarioID="scenario4",
                 pickedScenario=0,
                 nRepeat=1):
        
        self.name = "CogMod-Repeat"
        self.scenarioID = scenarioID
        self.researchSettings = CogModSettings(scenarioID)
        self.filterCarFollow = FilterCarFollow(self.researchSettings)
        self.data_collector = DataCollectorCarFollowWithRepeat()
        
        self.mapName = self.researchSettings.getMapName()
        self.stableHeightPath = self.researchSettings.getStableHeightPath()
        self.laneID = self.researchSettings.getLaneID()
        self.pivot = self.researchSettings.getPivot()
        self.baseCogmodAgentSettings = self.researchSettings.getCogModAgentSettings()
        self.base_distance = self.researchSettings.getBaseDistance()
        
        self.follow_scenario = self.filterCarFollow.get_follow_meta()
        self.combined_df = self.filterCarFollow.get_combined_df()
        self.stable_height_dict = read_stable_height_dict(self.stableHeightPath)
        # print("follow scenario length : ", len(self.follow_scenario))
        
        self.left_lane_id, self.right_lane_id = get_left_right_lanes(self.combined_df)
        
        super().__init__(
            name = self.name,
            client=client,
            mapName=self.mapName,
            logLevel=logLevel,
            outputDir=outputDir,
            simulationMode=simulationMode,
            showSpawnPoints=True
        )
        
        self.max_tick = 0
        self.agent_list = {'ego': None, 'preceding': None}
        self.scenario_status = ScenarioState.PENDING
        self.frame_tracker = 0
        
        self.pickedScenario = pickedScenario
        self.follow_meta_df = self.follow_scenario.iloc[self.pickedScenario]
        self.start_frame = self.follow_meta_df['start_frame']
        self.end_frame = self.follow_meta_df['end_frame']
        self.ego_id = self.follow_meta_df['ego_id']
        self.preceding_id = self.follow_meta_df['preceding_id']
        self.nRepeat = nRepeat
        self.logger.info(f"create_simulation {self.pickedScenario}, {self.follow_meta_df.values}")
        self.isDriverChanged = False
        
        all_frames = self.combined_df[self.combined_df['frame'].between(self.start_frame, self.end_frame+1)]
        self.preceding_agent_df = all_frames[(all_frames['id'] == self.preceding_id)]
        self.ego_agent_df = all_frames[(all_frames['id'] == self.ego_id)]
        self.trigger_distance = self.follow_meta_df['start_distance']
        
        pass
    
    def create_simulation(self):
        
        self.logger.info(f"create_simulation {self.pickedScenario}, simulation left {self.nRepeat}")
                        
        preceding_agent = self.createTrajectoryFollowerAgent(agent_id=self.preceding_id,
                                                             trajectory_df=self.preceding_agent_df,
                                                             pivot=self.pivot,
                                                             stable_height_dict=self.stable_height_dict,
                                                             laneID=self.laneID)
        self.world.tick()
        
        distance = self.trigger_distance + self.base_distance
        self.current_cogmod_agent_settings = self.baseCogmodAgentSettings
        self.current_cogmod_agent_settings = DriverModifier.change_cogmod_settings_pending_simulation(preceding_agent=preceding_agent,
                                                                                                      spawn_distance=distance,
                                                                                                      tracking_distance=self.trigger_distance,
                                                                                                      cogmod_settings=self.current_cogmod_agent_settings,
                                                                                                      ego_agent_df=self.ego_agent_df)
        
        print("current cogmod settings : ", self.current_cogmod_agent_settings['source'])
        ego_agent = self.createCogModAgent(self.current_cogmod_agent_settings, loglevel=logging.ERROR)
        self.agent_list = {'ego': ego_agent, 'preceding': preceding_agent}
        self.isDriverChanged = False
        pass
    
    
    # def get_trigger_distance_for_scenario(self, df):
        
    #     preceding_id, ego_id, start_frame = df['preceding_id'], df['ego_id'], df['start_frame']
        
    #     preceding_agent_df = self.follow_meta_df[(self.follow_meta_df['id'] == preceding_id) & (self.follow_meta_df['frame'] == start_frame)]
    #     ego_agent_df = self.follow_meta_df[(self.follow_meta_df['id'] == ego_id) & (self.follow_meta_df['frame'] == start_frame)]

    #     xPre, yPre = preceding_agent_df[['x', 'y']].values[0]
    #     xEgo, yEgo = ego_agent_df[['x', 'y']].values[0]
    #     scenario_trigger_distance = np.sqrt((xPre-xEgo)**2 + (yPre-yEgo)**2)
    
    #     return scenario_trigger_distance
    
    
    def run(self, maxTicks=100):
        self.max_tick = maxTicks
        self.create_simulation()
        
        onTickers = [self.UpdateScenarioStatus, self.dataCollectorOnTick, self.onTick]
        # onTickers = [self.UpdateScenarioStatus, self.onTick]
        onEnders = [self.onEnd]
        self.simulator = Simulator(self.client, onTickers=onTickers, onEnders=onEnders, simulationMode=self.simulationMode)
        self.simulator.run(maxTicks=maxTicks)
        pass
    
    def onEnd(self):
        print('onEnd')
        all_vehicle_actors = self.world.get_actors().filter('vehicle.*')
        id_list = []
        for actor in all_vehicle_actors:
            id_list.append(actor.id)
        print("all vehicle ids : ", id_list)
        command_list = []
        for id in id_list:
            command_list.append(carla.command.DestroyActor(id))
        res = self.client.apply_batch_sync(command_list, True)
        
        for r in res:
            if r.error:
                print('actor ', r.actor_id, r.error)
            else:
                print('actor ', r.actor_id, 'destroyed')
        pass
    
    def onTick(self, tick):
        
        # if tick goes beyond max tick, save data and exit
        if tick >= self.max_tick:
            dateStr = date.now().strftime("%Y-%m-%d-%H-%M-%S")
            self.data_collector.saveCSV(dateStr, self.outputDir)
            self.logger.info("simulation ended saving data....")
            exit()
        if self.agent_list['ego'] is None or self.agent_list['preceding'] is None:
            return
        
        ego_agent = self.agent_list['ego']
        preceding_agent = self.agent_list['preceding']
        del_t = self.time_delta # access the time delta from base class
        # print('del_t : ', del_t)

        ego_vehicle = ego_agent.vehicle
        preceding_vehicle = preceding_agent.vehicle

        ego_location = ego_vehicle.get_location()
        preceding_location = preceding_vehicle.get_location()

        # distance = preceding_location.distance(ego_location)
        # camera_location = (ego_location + preceding_location) / 2

        self.SetSpectator(ego_location, height=200)
        # print('cogmod speed:     ', round(ego_vehicle.get_velocity().length(), 2))
        if self.scenario_status == ScenarioState.START:
            if not self.isDriverChanged:
                cogmod_settings = DriverModifier.change_cogmod_settings_start_simulation(self.current_cogmod_agent_settings,
                                                                            self.ego_agent_df)
                ego_agent.reset_driver(cogmod_settings['driver_profile'], time_delta=0.04)
                self.isDriverChanged = True
                pass
            ego_control = ego_agent.run_step(del_t)
            if ego_control is not None:
                self.client.apply_batch_sync([carla.command.ApplyVehicleControl(ego_vehicle.id, ego_control)])
                pass
            # frame = self.start_frame + tick - self.frame_tracker
            # preceding_agent.run_step(frame)
            # AgentViz.draw_ego(frame, self.combined_df, self.ego_id, self.left_lane_id, 
            #                       self.world.debug, self.pivot, True)
            pass
        
        if self.scenario_status == ScenarioState.RUNNING:
            ego_control = ego_agent.run_step(del_t)
            if ego_control is not None:
                self.client.apply_batch_sync([carla.command.ApplyVehicleControl(ego_vehicle.id, ego_control)])
                pass
            frame = self.start_frame + tick - self.frame_tracker
            preceding_agent.run_step(frame)
            AgentViz.draw_ego(frame, self.combined_df, self.ego_id, self.left_lane_id, 
                                  self.world.debug, self.pivot, True)
            pass
        
        if self.scenario_status == ScenarioState.PENDING:
            ego_control = ego_agent.run_step(del_t)
            # print('cogmod speed:     ', round(ego_vehicle.get_velocity().length(), 2), 'target_speed', self.ego_agent_df['xVelocity'].iloc[0])
            if ego_control is not None:
                self.client.apply_batch_sync([carla.command.ApplyVehicleControl(ego_vehicle.id, ego_control)])
                pass
        
        if self.scenario_status == ScenarioState.END:
            self.onEnd()
            self.restart_scenario()
            pass
        
        pass
    
    
    def UpdateScenarioStatus(self, tick):
        
        ego_agent = self.agent_list['ego']
        preceding_agent = self.agent_list['preceding']
        
        ego_vehicle = ego_agent.vehicle
        preceding_vehicle = preceding_agent.vehicle
        ego_location = ego_vehicle.get_location()
        preceding_location = preceding_vehicle.get_location()
        ego_velocity = ego_vehicle.get_velocity().length()
        target_velocity = self.ego_agent_df['xVelocity'].iloc[0]
        
        distance = preceding_location.distance(ego_location)

        self.logger.info(f"{self.scenario_status}, tick: {tick} distance: {round(distance,2)}, target: {target_velocity}, cur: {round(ego_velocity,2)}")
        
        if ego_agent is None or preceding_agent is None:
            self.scenario_status = ScenarioState.END
            return 
        
        if ego_velocity >= target_velocity  and self.scenario_status == ScenarioState.PENDING:
            self.scenario_status = ScenarioState.START
            return
        
        # starting scenario if distance is less than trigger distance and scenario is pending
        if distance < self.trigger_distance and self.scenario_status == ScenarioState.START:
            self.scenario_status = ScenarioState.RUNNING
            self.frame_tracker = tick
            return
            
        cur_frame = tick - self.frame_tracker + self.start_frame
        if cur_frame > self.end_frame and self.scenario_status == ScenarioState.RUNNING:
            self.scenario_status = ScenarioState.END
            # print('scenario end')
        return 
    
    
    def restart_scenario(self):
        # TODO: restart the scenario
        # actor_list = self.world.get_actors()
        # vehicle_list = actor_list.filter("*vehicle*")
        # self.logger.info(f"destroying {len(vehicle_list)} vehicles")
        # for agent in vehicle_list:
        #     agent.destroy()
        # self.world.tick()
        if self.nRepeat == 0:
            print('scenario simulated for all repeats')
            dateStr = date.now().strftime("%Y-%m-%d-%H-%M-%S")
            dateStr = dateStr + '---' + str(self.pickedScenario)
            self.data_collector.saveCSV(dateStr, self.outputDir)
            self.logger.info("simulation ended saving data....")
            exit()
            pass
        elif self.nRepeat > 0:
            self.scenario_status = ScenarioState.PENDING
            self.nRepeat -= 1
            try:
                self.create_simulation()
            except Exception as e:
                self.logger.error(f"error in creating simulation {e}")
                self.onEnd()
                self.restart_scenario()
                
                
    def dataCollectorOnTick(self, tick):
        scenario_status = self.scenario_status
        scenario_id = self.pickedScenario
        exec_run = self.nRepeat
        if scenario_status == ScenarioState.PENDING or \
            scenario_status == ScenarioState.START or \
                scenario_status == ScenarioState.RUNNING:

            self.data_collector.collectStats(tick,
                                            self.ego_id,
                                            self.preceding_id,
                                            self.agent_list['ego'], 
                                            self.agent_list['preceding'],
                                            scenario_id,
                                            self.scenario_status,
                                            exec_num=exec_run)
            return
        if scenario_status == ScenarioState.END:
            self.data_collector.updateTrajectoryDF()
            pass
        pass