
import carla
from highd_tools.highD.DataHandler import *
from datetime import datetime as date
import logging
from lib import SimulationMode, Simulator
from research.BaseCogModResearch import BaseCogModResearch
from settings.CogModSettings import CogModSettings
from highd_tools.highD.Filter import FollowType
from agents.vehicles.TrajectoryAgent.helper import HighD_Processor
from analytics.DataCollectorCarFollowWithRepeat import DataCollectorCarFollowWithRepeat
from .ResearchCogMod import ScenarioState


class FilterCarFollow():
    def __init__(self, cogmod_settings):
        
        self.cogmod_settings = cogmod_settings
        self.highDPath = self.cogmod_settings.getHighDPath()
        self.dataset_id = self.cogmod_settings.getDatasetID()
        self.car_follow_settings = self.cogmod_settings.getCarFollowSettings()
        
        self.highD = read_dataset([self.dataset_id], self.highDPath)
        self.tracks = self.highD[0].tracks
        
        self.thw_lower_bound = self.car_follow_settings['thw_lower_bound']
        self.thw_upper_bound = self.car_follow_settings['thw_upper_bound']
        self.time_duration = self.car_follow_settings['time_duration']
        self.distance_threshold = self.car_follow_settings['distance_threshold']
        
        self.follow_meta = self.highD[0].get_vehicle_follow_meta(thw_lower_bound=self.thw_lower_bound,
                                                                 thw_upper_bound=self.thw_upper_bound,
                                                                 time_duration=self.time_duration,
                                                                 distance_threshold=self.distance_threshold)
        
        # self.car_car_follow = self.follow_meta[self.follow_meta['followType'] == FollowType.CAR_CAR]
        
    def get_car_car_follow(self):
        return self.car_car_follow
    
    def get_tracks(self):
        return self.tracks
    
    

class DriverModifier():

    @staticmethod
    def change_cogmod_settings_start_simulation(prev_cogmod_settings, ego_agent_df):
        cogmod_settings = prev_cogmod_settings
        velocity_df = np.sqrt(ego_agent_df['xVelocity']**2 + ego_agent_df['yVelocity']**2)

        positive_acceleration_df = ego_agent_df[ego_agent_df['xAcceleration'] >= 0]
        negative_acceleration_df = ego_agent_df[ego_agent_df['xAcceleration'] < 0]

        if not positive_acceleration_df.empty:
            max_acceleration = np.max(np.sqrt(positive_acceleration_df['xAcceleration']**2 + positive_acceleration_df['yAcceleration']**2)) * 3.6**2
        else:
            max_acceleration = 1

        if not negative_acceleration_df.empty:
            comfort_deceleration = np.nanmean(np.sqrt(negative_acceleration_df['xAcceleration']**2 + negative_acceleration_df['yAcceleration']**2)) * 3.6**2
        else:
            comfort_deceleration = 1

        desired_velocity = velocity_df.max()
        safe_time_headway = (1/ego_agent_df['dhw'].max()) * ego_agent_df['thw'].max() * 3.6**2 

        subtasks_parameters = cogmod_settings['driver_profile']['subtasks_parameters']
        lane_following_subtask = subtasks_parameters['lane_following']

        lane_following_subtask['desired_velocity'] = desired_velocity
        lane_following_subtask['safe_time_headway'] = 0
        lane_following_subtask['max_acceleration'] = max_acceleration
        lane_following_subtask['comfort_deceleration'] = comfort_deceleration

        subtasks_parameters['lane_following'] = lane_following_subtask
        cogmod_settings['driver_profile']['subtasks_parameters'] = subtasks_parameters

        return cogmod_settings

    @staticmethod
    def change_cogmod_settings_pending_simulation(preceding_agent, scenario_trigger_distance, base_distance, cogmod_settings):
        map = preceding_agent.vehicle.get_world().get_map()
        preceding_agent_location = preceding_agent.vehicle.get_location()
        nearest_waypoint_preceding_agent = map.get_waypoint(preceding_agent_location, project_to_road=True)

        distance = scenario_trigger_distance + base_distance
        spawn_waypoint = nearest_waypoint_preceding_agent.previous(distance)[0]
        spawn_transform = spawn_waypoint.transform
        spawn_location = spawn_transform.location

        destination_transform = preceding_agent.get_destination_transform()
        destination_waypoint = map.get_waypoint(destination_transform.location, project_to_road=True)
        destination_location = destination_waypoint.transform.location

        cogmod_settings['source'] = spawn_location
        cogmod_settings['destination'] = destination_location

        lane_following_subtask = cogmod_settings['driver_profile']['subtasks_parameters']['lane_following']
        lane_following_subtask['desired_velocity'] = 50
        lane_following_subtask['safe_time_headway'] = 0
        lane_following_subtask['max_acceleration'] = 20
        lane_following_subtask['comfort_deceleration'] = 0.5

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
            print('ego speed in data ', round(np.sqrt(xVel**2 + yVel**2), 2))
            pass  # Do something with the speed
        
    @staticmethod
    def transform_coordinate_wrt_pivot(row, pivot):
        x, y, width, height = row[["x", "y", "width", "height"]]
        center_x = float(x + width/2 + pivot.location.x)
        center_y = float(y + height/2 + pivot.location.y)
        return center_x, center_y


class ResearchCarFollowRepeat(BaseCogModResearch):
    def __init__(self, 
                 client, 
                 logLevel=logging.INFO, 
                 outputDir="logs", 
                 simulationMode=SimulationMode.SYNCHRONOUS, 
                 scenarioID="scenario4",
                 pickedScenario=0,
                 nRepeat=1):
        
        self.name = "CogMod-HighD"
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
        
        self.car_car_follow = self.filterCarFollow.get_car_car_follow()
        self.tracks = self.filterCarFollow.get_tracks()
        self.stable_height_dict = HighD_Processor.read_stable_height_dict(self.stableHeightPath)
        print("car_car_follow length : ", len(self.car_car_follow))
        
        self.left_lane_id = set(self.laneID['left_lane'])
        self.right_lane_id = set(self.laneID['right_lane'])
        
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
        self.df = self.car_car_follow.iloc[self.pickedScenario]
        self.start_frame = self.df['start_frame']
        self.end_frame = self.df['end_frame']
        self.ego_id = self.df['ego_id']
        self.preceding_id = self.df['preceding_id']
        self.nRepeat = nRepeat
        self.logger.info(f"create_simulation {self.pickedScenario}, {self.df.values}")
        
        all_frames = self.tracks[self.tracks['frame'].between(self.start_frame, self.end_frame+1)]
        self.preceding_agent_df = all_frames[(all_frames['id'] == self.preceding_id)]
        self.ego_agent_df = all_frames[(all_frames['id'] == self.ego_id)]
        self.trigger_distance = self.get_trigger_distance_for_scenario(self.df)
        pass
    
    def create_simulation(self):
        
        self.logger.info(f"create_simulation {self.pickedScenario}, simulation left {self.nRepeat}")
                        
        preceding_agent = self.createTrajectoryFollowerAgent(agent_id=self.preceding_id,
                                                             trajectory_df=self.preceding_agent_df,
                                                             pivot=self.pivot,
                                                             stable_height_dict=self.stable_height_dict,
                                                             laneID=self.laneID)
        self.world.tick()
        
        self.current_cogmod_agent_settings = self.baseCogmodAgentSettings
        self.current_cogmod_agent_settings = DriverModifier.change_cogmod_settings_pending_simulation(preceding_agent,
                                                                                                    self.trigger_distance,
                                                                                                    base_distance=self.base_distance,
                                                                                                    cogmod_settings=self.current_cogmod_agent_settings)
        
        ego_agent = self.createCogModAgent(self.current_cogmod_agent_settings)
        self.agent_list = {'ego': ego_agent, 'preceding': preceding_agent}
        
        pass
    
    
    def get_trigger_distance_for_scenario(self, df):
        
        preceding_id, ego_id, start_frame = df['preceding_id'], df['ego_id'], df['start_frame']
        
        preceding_agent_df = self.tracks[(self.tracks['id'] == preceding_id) & (self.tracks['frame'] == start_frame)]
        ego_agent_df = self.tracks[(self.tracks['id'] == ego_id) & (self.tracks['frame'] == start_frame)]

        xPre, yPre = preceding_agent_df[['x', 'y']].values[0]
        xEgo, yEgo = ego_agent_df[['x', 'y']].values[0]
        scenario_trigger_distance = np.sqrt((xPre-xEgo)**2 + (yPre-yEgo)**2)
    
        return scenario_trigger_distance
    
    
    def run(self, maxTicks=100):
        self.max_tick = maxTicks
        self.create_simulation()
        
        onTickers = [self.UpdateScenarioStatus, self.dataCollectorOnTick, self.onTick]
        # onTickers = [self.UpdateScenarioStatus, self.onTick]
        onEnders = [self.onEnd]
        self.simulator = Simulator(self.client, onTickers=onTickers, onEnders=onEnders, simulationMode=self.simulationMode)
        self.simulator.run(maxTicks=maxTicks)
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

        ego_vehicle = ego_agent.vehicle
        preceding_vehicle = preceding_agent.vehicle

        ego_location = ego_vehicle.get_location()
        preceding_location = preceding_vehicle.get_location()

        # distance = preceding_location.distance(ego_location)
        # camera_location = (ego_location + preceding_location) / 2

        self.SetSpectator(ego_location, height=200)
        print('cogmod speed:     ', round(ego_vehicle.get_velocity().length(), 2))
        if self.scenario_status == ScenarioState.START:
            # change the cogmod setting at the start of the simulation
            cogmod_settings = DriverModifier.change_cogmod_settings_start_simulation(self.current_cogmod_agent_settings,
                                                                           self.ego_agent_df)
            # subtask = cogmod_settings['driver_profile']['subtasks_parameters']['lane_following']
            # self.logger.info(f'new setting {subtask}')
            ego_agent.reset_driver(cogmod_settings['driver_profile'])
            # apply control
            ego_control = ego_agent.run_step(del_t)
            if ego_control is not None:
                ego_vehicle.apply_control(ego_control)
                pass
            # start the scenario so move the preceding vehicle
            frame = self.start_frame + tick - self.frame_tracker
            preceding_agent.run_step(frame)
            AgentViz.draw_ego(frame, self.tracks, self.ego_id, self.left_lane_id, 
                                  self.world.debug, self.pivot, True)
            pass
        
        if self.scenario_status == ScenarioState.RUNNING:
            ego_control = ego_agent.run_step(del_t)
            if ego_control is not None:
                ego_vehicle.apply_control(ego_control)
                pass
            frame = self.start_frame + tick - self.frame_tracker
            preceding_agent.run_step(frame)
            AgentViz.draw_ego(frame, self.tracks, self.ego_id, self.left_lane_id, 
                                  self.world.debug, self.pivot, True)
            pass
        
        if self.scenario_status == ScenarioState.PENDING:
            ego_control = ego_agent.run_step(del_t)
            # print('cogmod speed:     ', round(ego_vehicle.get_velocity().length(), 2))
            if ego_control is not None:
                ego_vehicle.apply_control(ego_control)
                pass
        
        if self.scenario_status == ScenarioState.END:
            # self.simulator.onEnd()
            self.restart_scenario()
            pass
        
        pass
    
    
    def UpdateScenarioStatus(self, tick):
        
        ego_agent = self.agent_list['ego']
        preceding_agent = self.agent_list['preceding']

        if ego_agent is None or preceding_agent is None:
            self.scenario_status = ScenarioState.END
            return 
        if self.scenario_status == ScenarioState.START:
            self.scenario_status = ScenarioState.RUNNING
            return
        
        ego_vehicle = ego_agent.vehicle
        preceding_vehicle = preceding_agent.vehicle
        ego_location = ego_vehicle.get_location()
        preceding_location = preceding_vehicle.get_location()

        distance = preceding_location.distance(ego_location)
        
        # starting scenario if distance is less than trigger distance and scenario is pending
        if distance < self.trigger_distance and self.scenario_status == ScenarioState.PENDING:
            self.scenario_status = ScenarioState.START
            self.frame_tracker = tick
            return
            
        cur_frame = tick - self.frame_tracker + self.start_frame
        if cur_frame > self.end_frame and self.scenario_status == ScenarioState.RUNNING:
            self.scenario_status = ScenarioState.END
            # print('scenario end')
        return 
    
    
    def restart_scenario(self):
        
        actor_list = self.world.get_actors()
        vehicle_list = actor_list.filter("*vehicle*")
        self.logger.info(f"destroying {len(vehicle_list)} vehicles")
        for agent in vehicle_list:
            agent.destroy()
        self.world.tick()
        
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
                # self.simulator.onEnd()
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