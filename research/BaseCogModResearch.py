import carla
from lib.exceptions import NotImplementedInterface
from .BaseResearch import BaseResearch
from agents.vehicles import VehicleFactory
from agents.vehicles.CogMod.CogModAgent import CogModAgent
from agents.vehicles.TrajectoryAgent import TrajectoryAgent
from agents.vehicles.TrajectoryAgent import TrajectoryFollower


class BaseCogModResearch(BaseResearch):

    def __init__(self,
                 name,
                 client,
                 mapName,
                 logLevel,
                 outputDir,
                 simulationMode,
                 showSpawnPoints=False):
        super().__init__(name,
                         client,
                         mapName,
                         logLevel,
                         outputDir,
                         simulationMode)
        
        # contains all the agents with id as key
        self.agent_list = {}

        self.vehicle_factory =  VehicleFactory(client)

        if showSpawnPoints:
            self.visualizer.drawAllSpawnPointsWithText()
        
        pass
    
    def onStart(self):
        raise NotImplementedInterface("onStart")

    def onTick(self, world_snapshot):
        for agent_id, agent in self.agent_list.items():
            control = agent.run_step()
            if control is not None:
                agent.get_vehicle().apply_control(control)
        # self.logger.info(f"ticked all agents {world_snapshot.frame}")
        
        pass

    def onEnd(self):
        self.logger.info("Ending simulation")
        self.logger.info(f"length of vehicle list {len(self.agent_list)}")
        
        for agent_id, agent in self.agent_list.items():
            self.logger.info(f"destroying agent {agent_id}")
            agent.get_vehicle().destroy()
        self.agent_list.clear()
        self.logger.info("destroyed all vehicles")
        pass

    def run(self, maxTicks=100):
        raise NotImplementedInterface("run")
    
    # in synchronous mode if we dont tick the vehicle is spawned on origin (0, 0)
    #  right after tick vehicle is shifted at the correct location
    def createCogModAgent(self, agent_settings):
        # self.logger.info("createCogModAgent")
        spawn_wp = self.LocationToWaypoint(agent_settings['source'])
        destination_wp = self.LocationToWaypoint(agent_settings['destination'])
        driver_profile = agent_settings['driver_profile']

        vehicle = self.vehicle_factory.spawn(spawn_wp)
        if vehicle is None:
            self.logger.error(f"Cannot create vehicle - stopping simulation")
            exit("cannot spawn cogmod vehicle")
        else:
            self.logger.info(f"successfully spawned cogmod actor {vehicle.id}")
            self.world.tick()
            # self.logger.info(f"vehicle location {vehicle.get_location()}")
            cogmod_agent = CogModAgent(vehicle=vehicle, 
                                       destination_point=destination_wp, 
                                       driver_profile=driver_profile)
            self.agent_list[vehicle.id] = cogmod_agent
            return cogmod_agent
        

    def createTrajectoryAgent(self, agent_id, tracksDF, pivot, spawn_height=0.5):
        
        # get all row from tracks with agent_id
        agent_tracks = tracksDF[tracksDF['id'] == agent_id]
        # get the first row
        first_row = agent_tracks.iloc[0]
        x, y, width, height = first_row['x'], first_row['y'], first_row['width'], first_row['height']
        # create a spawn location
        spawn_location = carla.Location(x=x, y=y, z=spawn_height)
        rotation = carla.Rotation()
        spawn_transform = carla.Transform(spawn_location, rotation)
        # spawn the vehicle
        vehicle = self.vehicle_factory.spawn(spawn_transform)
        if vehicle is None:
            self.logger.error(f"Cannot create vehicle - stopping simulation")
            exit("cannot spawn trajectory vehicle")
        else:
            self.logger.info(f"successfully spawned trajectory actor {vehicle.id}")
            trajectory_agent = TrajectoryAgent(vehicle=vehicle,
                                               pivot=pivot,
                                               agent_id=agent_id)
            self.agent_list[agent_id] = trajectory_agent
            return trajectory_agent

    def createTrajectoryFollowerAgent(self, agent_id, trajectory_df, pivot, stable_height_dict, laneID=None):

        # get the first row
        first_row = trajectory_df.iloc[0]
        x, y = first_row['x'], first_row['y']
        # create a spawn location
        spawn_location = carla.Location(x=x, y=y, z=0.5)
        rotation = carla.Rotation()
        spawn_transform = carla.Transform(spawn_location, rotation)
        # spawn the vehicle
        vehicle = self.vehicle_factory.spawn(spawn_transform)
        if vehicle is None:
            self.logger.error(f"Cannot create vehicle - stopping simulation")
            exit("cannot spawn trajectory vehicle")
        else:
            self.logger.info(f"successfully spawned trajectory actor {vehicle.id}")
            stable_height = stable_height_dict[vehicle.type_id]
            trajectory_follower = TrajectoryFollower(vehicle=vehicle,
                                                     trajectory_df=trajectory_df,
                                                     pivot=pivot,
                                                     agent_id=agent_id,
                                                     stable_height=stable_height,
                                                     lane_id=laneID)
            self.agent_list[agent_id] = trajectory_follower
            return trajectory_follower

        pass

    def createActorAgent(self, agent_settings):
        self.logger.info(f"creating actor agent")
        spawn_wp = self.LocationToWaypoint(agent_settings['source'])
        destination_wp = self.LocationToWaypoint(agent_settings['destination'])
        driver_profile = agent_settings['driver_profile']

        vehicle = self.vehicle_factory.spawn(spawn_wp)
        if vehicle is None:
            self.logger.error(f"Cannot create actor vehicle - stopping simulation")
            exit("cannot spawn actor vehicle")
        else:
            self.logger.info(f"successfully spawned actor actor {vehicle.id}")
            actor_agent = self.vehicle_factory.createBehaviorAgent(vehicle=vehicle,
                                                                   behavior=driver_profile)
            actor_agent.set_destination(destination_wp.location)
            self.agent_list[vehicle.id] = actor_agent
            return actor_agent
        pass
    
    def LocationToWaypoint(self, location):
        waypoint = self.map.get_waypoint(location, 
                                         project_to_road=True, 
                                         lane_type=carla.LaneType.Driving)
        if waypoint is None:
            msg = f"{self.name}: Cannot create way point near {location}"
            self.error(msg)
        transform = carla.Transform(location = waypoint.transform.location + carla.Location(z=1), rotation = waypoint.transform.rotation)
        return transform


    def SetSpectator(self, location, rotation=None, height=100):
        spectator = self.world.get_spectator()
        location = carla.Location(x=location.x, y=location.y, z=height)
        if rotation is None:
            rotation = carla.Rotation(pitch=-90, yaw=0)
        
        spectator.set_transform(carla.Transform(location, rotation))
        pass
    
