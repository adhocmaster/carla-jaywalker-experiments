
import carla
from highd_tools.highD.DataHandler import *
from datetime import datetime as date
import logging
from lib import SimulationMode, Simulator
from research.BaseCogModResearch import BaseCogModResearch
from settings.CogModSettings import CogModSettings
from highd_tools.highD.ManeuverFilter import FollowType
from agents.vehicles.TrajectoryAgent.helper import HighD_Processor
from analytics.DataCollectorCarFollow import DataCollectorCarFollow
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
        
        self.car_car_follow = self.follow_meta[self.follow_meta['followType'] == FollowType.CAR_CAR]
        
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
        lane_following_subtask['desired_velocity'] = 40
        lane_following_subtask['safe_time_headway'] = 0
        lane_following_subtask['max_acceleration'] = 10
        lane_following_subtask['comfort_deceleration'] = 1

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


class ResearchCarFollow(BaseCogModResearch):
    def __init__(self, 
                 client, 
                 logLevel=logging.INFO, 
                 outputDir="logs", 
                 simulationMode=SimulationMode.SYNCHRONOUS, 
                 scenarioID="scenario4"):
        
        self.name = "CogMod-HighD"
        self.scenarioID = scenarioID
        self.researchSettings = CogModSettings(scenarioID)
        self.filterCarFollow = FilterCarFollow(self.researchSettings)
        self.data_collector = DataCollectorCarFollow()
        
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
        
        self.bug_list = [] # 19
        self.scenario_list_df = [i for i in range(0, len(self.car_car_follow))] 
        
        self.current_scenario_id = 2
        self.max_tick = 0
        self.agent_list = {'ego': None, 'preceding': None}
        self.scenario_status = ScenarioState.PENDING
        self.frame_tracker = 0
        self.scenario_start_frame = 0
        
        self.ego_agent_df = None
        self.preceding_agent_df = None
        self.ego_id = None
        self.preceding_id = None
        self.trigger_distance = None
        
        pass
    
    def create_simulation(self, scenario_id):
        self.logger.info(f"create_simulation {scenario_id}, {self.car_car_follow.iloc[scenario_id].values}")
        df = self.car_car_follow.iloc[scenario_id]
        start_frame, end_frame, ego_id, preceding_id = df['start_frame'], df['end_frame'], df['ego_id'], df['preceding_id']
        
        all_frames = self.tracks[self.tracks['frame'].between(start_frame, end_frame+1)]
        trigger_distance = self.get_trigger_distance(df)
        
        preceding_agent_df = all_frames[(all_frames['id'] == preceding_id)]
        ego_agent_df = all_frames[(all_frames['id'] == ego_id)]
        preceding_agent = self.createTrajectoryFollowerAgent(agent_id=preceding_id,
                                                             trajectory_df=preceding_agent_df,
                                                             pivot=self.pivot,
                                                             stable_height_dict=self.stable_height_dict,
                                                             laneID=self.laneID)
        self.world.tick()
        
        cogmod_modifier = DriverModifier()
        self.current_cogmod_agent_settings = self.baseCogmodAgentSettings
        self.current_cogmod_agent_settings = cogmod_modifier.change_cogmod_settings_pending_simulation(preceding_agent,
                                                                                                    trigger_distance,
                                                                                                    base_distance=self.base_distance,
                                                                                                    cogmod_settings=self.current_cogmod_agent_settings)
        
        ego_agent = self.createCogModAgent(self.current_cogmod_agent_settings)
        
        self.agent_list = {'ego': ego_agent, 'preceding': preceding_agent}
        
        self.preceding_agent_df = preceding_agent_df
        self.ego_agent_df = ego_agent_df
        self.ego_id = ego_id
        self.preceding_id = preceding_id
        
        self.scenario_start_frame = start_frame
        self.scenario_end_frame = end_frame
        
        self.trigger_distance = trigger_distance
        pass
    
    
    def get_trigger_distance(self, df):
        
        preceding_id, ego_id, start_frame = df['preceding_id'], df['ego_id'], df['start_frame']
        
        preceding_agent_df = self.tracks[(self.tracks['id'] == preceding_id) & (self.tracks['frame'] == start_frame)]
        ego_agent_df = self.tracks[(self.tracks['id'] == ego_id) & (self.tracks['frame'] == start_frame)]

        xPre, yPre = preceding_agent_df[['x', 'y']].values[0]
        xEgo, yEgo = ego_agent_df[['x', 'y']].values[0]
        scenario_trigger_distance = np.sqrt((xPre-xEgo)**2 + (yPre-yEgo)**2)
    
        return scenario_trigger_distance
    
    
    def run(self, maxTicks=100):
        self.max_tick = maxTicks
        self.create_simulation(self.current_scenario_id)
        # onTickers = [self.UpdateScenarioStatus, self.dataCollectorOnTick, self.onTick]
        
        onTickers = [self.UpdateScenarioStatus, self.onTick]
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
        if self.scenario_status == ScenarioState.PENDING or \
            self.scenario_status == ScenarioState.START or \
                self.scenario_status == ScenarioState.RUNNING:

            ego_control = ego_agent.run_step(del_t)
            speed = ego_vehicle.get_velocity().length()
            print('cogmod speed:     ', round(speed, 2))
            if ego_control is not None:
                ego_vehicle.apply_control(ego_control)
                pass
            if self.scenario_status == ScenarioState.START or \
                self.scenario_status == ScenarioState.RUNNING:
                cur_tick = tick - self.frame_tracker
                frame = self.scenario_start_frame + cur_tick
                # print(f"frame: {frame}, tick: {tick}, frame_tracker: {self.frame_tracker}, start_frame: {self.scenario_start_frame}")
                preceding_agent.run_step(frame)
                
                AgentViz.draw_ego(frame, self.tracks, self.ego_id, self.left_lane_id, 
                                  self.world.debug, self.pivot, True)
                self.scenario_status = ScenarioState.RUNNING
                pass

        if self.scenario_status == ScenarioState.END:
            self.simulator.onEnd()
            self.restart_scenario()
            pass
        
        pass
    
    
    def UpdateScenarioStatus(self, tick):
        
        ego_agent = self.agent_list['ego']
        preceding_agent = self.agent_list['preceding']

        if ego_agent is None or preceding_agent is None:
            self.scenario_status = ScenarioState.END
            return 
        
        ego_vehicle = ego_agent.vehicle
        preceding_vehicle = preceding_agent.vehicle

        ego_location = ego_vehicle.get_location()
        preceding_location = preceding_vehicle.get_location()

        distance = preceding_location.distance(ego_location)
        # print(f"distance {distance}, trigger distance {self.trigger_distance}")
        if distance < self.trigger_distance :
            if self.scenario_status == ScenarioState.PENDING:
                self.frame_tracker = tick

                self.scenario_status = ScenarioState.START
                cogmod_settings = DriverModifier.change_cogmod_settings_start_simulation(self.current_cogmod_agent_settings,
                                                                               self.ego_agent_df)
                subtask = cogmod_settings['driver_profile']['subtasks_parameters']['lane_following']
                self.logger.info(f'new setting {subtask}')
                ego_agent.reset_driver(cogmod_settings['driver_profile'])


        # print(f'tick + ft {tick - self.frame_tracker + self.scenario_start_frame}, scenario end {self.scenario_end_frame}')
        cur_frame = tick - self.frame_tracker + self.scenario_start_frame
        if self.scenario_status == ScenarioState.RUNNING:
            if cur_frame > self.scenario_end_frame:
                print('scenario end')
                self.scenario_status = ScenarioState.END
        return 
    
    
    def restart_scenario(self):
        
        actor_list = self.world.get_actors()
        vehicle_list = actor_list.filter("*vehicle*")
        self.logger.info(f"destroying {len(vehicle_list)} vehicles")
        for agent in vehicle_list:
            agent.destroy()

        self.world.tick()
        self.scenario_status = ScenarioState.PENDING
        current_scenario_id = self.current_scenario_id
        self.current_scenario_id += 1
        if current_scenario_id >= len(self.car_car_follow):
            print('all scenarios done')
            dateStr = date.now().strftime("%Y-%m-%d-%H-%M-%S")
            self.data_collector.saveCSV(dateStr, self.outputDir)
            self.logger.info("simulation ended saving data....")
            exit()
            return
        try:
            self.create_simulation(self.current_scenario_id)
        except Exception as e:
            self.bug_list.append(current_scenario_id)

            self.logger.error(f"error in creating simulation {e}")
            self.logger.error(f"scenario id: {current_scenario_id}")
            self.logger.error(f"bug list: {self.bug_list}")
            self.simulator.onEnd()
            self.restart_scenario()
        pass