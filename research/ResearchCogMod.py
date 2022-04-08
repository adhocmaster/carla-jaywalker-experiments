import math
import time
from unittest import result
import carla

from lib.MapManager import MapNames

from .BaseResearch import BaseResearch
from settings.t_junction_settings import t_junction_settings
from settings import SettingsManager
from agents.pedestrians import PedestrianFactory
from agents.vehicles import VehicleFactory
from lib import Simulator, SimulationMode
from lib import Utils

class ResearchCogMod(BaseResearch):

    def __init__(self, client: carla.Client, 
                 logLevel, 
                 mapName=MapNames.t_junction, 
                 outputDir:str = "logs", 
                 simulationMode = SimulationMode.ASYNCHRONOUS,
                 simulation_id = "setting1"):
        self.name = "Research CogMod"
        super().__init__(name=self.name, 
                         client=client, 
                         mapName=mapName, 
                         logLevel=logLevel, 
                         outputDir=outputDir,
                         simulationMode=simulationMode)

        self.simulation_id = simulation_id

        self.settingsManager = SettingsManager(self.client, t_junction_settings)
        self.vehicleFactory = VehicleFactory(self.client, visualizer=self.visualizer)

        self.number_of_cogmod_agents = 0
        self.number_of_actor_agents = 0


        self.vehicle_list = []
        self.cogmod_agent_list = []
        self.actor_agent_list = []

        self.cogmod_agent_parameter_list = []
        self.actor_trajectory_list = []
        
        self.setup()


    def setup(self):
        self.settingsManager.load(self.simulation_id)
        self.simulator = None # populated when run
        self.number_of_cogmod_agents, self.cogmod_agent_parameter_list = self.settingsManager.getNumberOfCogmodAgentsWithParameters()
        self.number_of_actor_agents, self.actor_trajectory_list = self.settingsManager.getNumberOfActorAgentsWithTrajectories()
        

        self.visualizer.drawSpawnPoints()

        # unique_lanes = {}
        # for wp in self.mapManager.waypoints:
        #     if wp.lane_id not in unique_lanes:
        #         unique_lanes[wp.lane_id] = True
        # print(f'unique roads {unique_lanes}')

        pass

    def onEnd(self):
        self.destoryActors()
    
    def destoryActors(self):
        for vehicle in self.vehicle_list:
            vehicle.destroy()
        self.cogmod_agent_list = []
        pass

    def destroyAgent(self, agent):
        self.cogmod_agent_list.remove(agent)
        self.vehicle_list.remove(agent.vehicle)
        agent.vehicle.destroy()

    def onTick(self, world_snapshot):
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.updateVehiclesAsynchoronousMode(world_snapshot)
        if self.simulationMode == SimulationMode.SYNCHRONOUS:
            self.updateVehiclesSynchoronousMode(world_snapshot)

        for agent in self.cogmod_agent_list:
            print(f'agent : {agent.vehicle.id}, lm {len(agent.longterm_memory.request_queue)}, cc {len(agent.complex_cognition.request_queue)}, mc {len(agent.motor_control.request_queue)}')
            # print(f'lm {len(agent.longterm_memory.request_queue)}')
            # print(f'cc {len(agent.complex_cognition.request_queue)}')
            # print(f'mc {len(agent.motor_control.request_queue)}')

        



    #region simulation
    def run(self, maxTicks=5000):
        print('inside run research')
        
        
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.createCogmodAgentAsynchronousMode()
            self.createActorAgentsAsynchronousMode()
            self.world.wait_for_tick()
        if self.simulationMode == SimulationMode.SYNCHRONOUS:
            self.createCogmodAgentSynchronousMode()
            # self.createActorAgentsSynchronousMode()
            self.world.tick()
        
        for agent in self.cogmod_agent_list:
            print(f'agent : {agent}')
            self.visualizer.trackAgentOnTick(agent)

        onTickers = [self.visualizer.onTick, self.onTick]
        onEnders = [self.onEnd]
        self.simulator = Simulator(self.client, onTickers=onTickers, onEnders=onEnders, simulationMode=self.simulationMode)

        self.simulator.run(maxTicks)

        # try: 
        # except Exception as e:
        #     self.logger.exception(e)
        pass


    def createActorAgentsAsynchronousMode(self):
        for i in range(self.number_of_actor_agents):
            trajectory = self.actor_trajectory_list[i]
            spawn_point = trajectory[0].first
            vehicle = self.vehicleFactory.spawn(spawnPoint=spawn_point)
            if vehicle is None:
                self.logger.error("Could not spawn a vehicle")
                exit("cannot spawn a vehicle")
                return
            else:
                self.logger.info(f"successfully spawn vehicle {vehicle.id} at {spawn_point.location.x, spawn_point.location.y, spawn_point.location.z}")
            self.vehicle_list.append(vehicle)

            actor_agent = self.vehicleFactory.createActorAgent(id=len(self.vehicle_list),
                                                               vehicle=vehicle, 
                                                               trajectory=trajectory)
            self.actor_agent_list.append(actor_agent)
            pass
        pass

    

    def createCogmodAgentAsynchronousMode(self):       

        for i in range(self.number_of_cogmod_agents):
            spawn_point = self.cogmod_agent_parameter_list[i]['spawn_point']
            destination_point = self.cogmod_agent_parameter_list[i]['destination_point']
            driver_profile = self.cogmod_agent_parameter_list[i]['driver_profile']
           
            # spawn the vehicle in the simulator
            vehicle = self.vehicleFactory.spawn(spawn_point)
            if vehicle is None:
                self.logger.error("Could not spawn a vehicle")
                exit("cannot spawn a vehicle")
                return
            else:
                self.logger.info(f"successfully spawn vehicle {vehicle.id} at {spawn_point.location.x, spawn_point.location.y, spawn_point.location.z}")
            

            self.vehicle_list.append(vehicle)

            # create the vehicle agent
            vehicleAgent = self.vehicleFactory.createCogModAgent(id=i,
                                                                 vehicle=vehicle,
                                                                 destinationPoint=destination_point,
                                                                 driver_profile=driver_profile)
                                                                 
            self.cogmod_agent_list.append(vehicleAgent)
            pass

        pass


    def createActorAgentsSynchronousMode(self):
        batch = []
        for i in range(self.number_of_actor_agents):
            trajectory = self.actor_trajectory_list[i]
            spawn_point = trajectory[0][0]
            spawn_command = self.vehicleFactory.spawn_command(spawnPoint=spawn_point)
            batch.append(spawn_command)
            pass

        results = self.client.apply_batch_sync(batch, True)

        for i in range(len(results)):
            result = results[i]
            if not result.error:
                vehicle_actor = self.world.get_actor(result.actor_id)
                actor_agent = self.vehicleFactory.createActorAgent(id=len(self.vehicle_list),
                                                                   vehicle=vehicle_actor,
                                                                   trajectory=self.actor_trajectory_list[i])
                self.vehicle_list.append(vehicle_actor)
                self.actor_agent_list.append(actor_agent)
                pass
            else:
                exit(f"failed to spawn vehicle {i}")
            pass
        pass

    # In the synchronous mode, the spawn command are applied in batch
    def createCogmodAgentSynchronousMode(self):       
        batch = []
        for i in range(self.number_of_cogmod_agents):
            spawn_point = self.cogmod_agent_parameter_list[i]['spawn_point']
            
            # creating the vehicle spawning command 
            spawn_command = self.vehicleFactory.spawn_command(spawn_point)
            batch.append(spawn_command)
            pass

        # applying all command togather 
        results = self.client.apply_batch_sync(batch, True)
        # print(f'results : {results}')

        for i in range(len(results)):
            if not results[i].error:
                print(f"successfully spawn vehicle {results[i].actor_id}")
                vehicle_actor = self.world.get_actor(results[i].actor_id)
                destination_point = self.cogmod_agent_parameter_list[i]['destination_point']
                driver_profile = self.cogmod_agent_parameter_list[i]['driver_profile']
                vehicleAgent = self.vehicleFactory.createCogModAgent(id=vehicle_actor.id,
                                                                     vehicle=vehicle_actor,
                                                                     destinationPoint=destination_point,
                                                                     driver_profile=driver_profile) 
                
                self.vehicle_list.append(vehicle_actor)                      
                self.cogmod_agent_list.append(vehicleAgent)
            else:
                exit(f"failed to spawn vehicle {i}")
                return
        pass
            
    def updateVehiclesSynchoronousMode(self, world_snapshot):
        batch = []
        if len(self.vehicle_list) == 0:
            self.logger.warn(f"No vehicle to update")
            exit()
            return

        agent_to_remove = []
        for agent in self.cogmod_agent_list:
            if agent.is_done():
                agent_to_remove.append(agent)
            else:
                control = agent.update_agent(self.cogmod_agent_list)
                if control is not None:
                    batch.append(carla.command.ApplyVehicleControl(agent.vehicle.id, control))

        split_index = len(batch)

        for agent in agent_to_remove:
            destroy_command = carla.command.DestroyActor(agent.vehicle.id)
            batch.append(destroy_command)
            
        results = self.client.apply_batch_sync(batch, True)
        for i in range(split_index, len(results)):
            print('destroy agent ')
            self.destroyAgent(self.cogmod_agent_list[i])
            pass
        pass


    def updateVehiclesAsynchoronousMode(self, world_snapshot):
        if len(self.vehicle_list) == 0:
            self.logger.warn(f"No vehicle to update")
            exit()
            return

        agent_to_remove = []
        for agent in self.cogmod_agent_list:
            if agent.is_done():
                agent_to_remove.append(agent)
            else:
                control = agent.update_agent(self.cogmod_agent_list)
                if control is not None:
                    agent.vehicle.apply_control(control)

        for agent in agent_to_remove:
            self.destroyAgent(agent)
            
  
        pass


