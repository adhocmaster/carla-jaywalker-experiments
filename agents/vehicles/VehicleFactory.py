import carla
import random
import logging


from agents.navigation.behavior_agent import BehaviorAgent  # pylint: disable=import-error
from agents.navigation.basic_agent import BasicAgent  # pylint: disable=import-error
from lib import LoggerFactory, ClientUser

from agents.vehicles.qnactr.CogMod import CogModAgent  # cogmod agent 
from .qnactr.TrajectoryFollower import TrajectoryFollower  # trajectory follower actor agent

from typing import List

from lib import LoggerFactory

class VehicleFactory(ClientUser):

    
    def __init__(self, client: carla.Client, time_delta=0.1, visualizer=None):
        
        self.name = "VehicleFactory"
        self.logger = LoggerFactory.create(self.name)
        super().__init__(client)

        
        self.vehicles = []

        self.visualizer = visualizer
        self.time_delta = time_delta
        
        self.bpLib = self.world.get_blueprint_library()
        # self.vehicleBps = self.bpLib.filter('vehicle.audi.*')
        self.vehicleBps = self.bpLib.filter('vehicle.*')
        
        self.tm = client.get_trafficmanager(8000)
        self.tm.set_global_distance_to_leading_vehicle(2.5)

        
    def getVehicles(self):
        return self.vehicles

        
    def create(self):
        vehicleBp = random.choice(self.vehicleBps)
        return vehicleBp

    
    def destroy(self, vehicle: carla.Vehicle):
        self.vehicles.remove(vehicle)
        vehicle.destroy()


    def reset(self):
        for vehicle in self.vehicles:
            self.destroy(vehicle)

    
    def spawn(self, spawnPoint: carla.Transform):

        if spawnPoint.location.z < 0.5:
           spawnPoint.location.z = 0.5 
        vehicleBp = self.create()
        vehicle = self.world.spawn_actor(vehicleBp, spawnPoint)
        self.vehicles.append(vehicle)
        return vehicle

    
    def batchSpawn(self, spawnPoints: carla.Transform):

        batch = []
        for spawnPoint in spawnPoints:
            if spawnPoint.location.z < 0.5:
                spawnPoint.location.z = 0.5 
                
            vehicleBp = self.create()
            batch.append(
                carla.command.SpawnActor(vehicleBp, spawnPoint)
                    .then(carla.command.SetAutopilot(carla.command.FutureActor, True, self.tm.get_port()))
            )

        
        generatedVehicles = []

        for response in self.client.apply_batch_sync(batch):
            if response.error:
                logging.error(response.error)
            else:
                generatedVehicles.append(self.world.get_actor(response.actor_id))
                self.vehicles.extend(generatedVehicles)
                
        return generatedVehicles

    
    def createAgent(self, vehicle: carla.Vehicle, target_speed=20, logLevel=logging.INFO) -> BasicAgent:
        agent = BasicAgent(vehicle, target_speed=20, opt_dict={"debug": True})
        return agent

    def createBehaviorAgent(self, vehicle: carla.Vehicle, behavior="normal", logLevel=logging.INFO) -> BehaviorAgent:
        agent = BehaviorAgent(vehicle, behavior=behavior)
        return agent


    def spawn_command(self, spawnPoint):
        vehicleBp = self.create()
        spawn_command = carla.command.SpawnActor(vehicleBp, spawnPoint)
        return spawn_command
    
    def createActorAgent(self, id, vehicle, trajectory):
        agent = TrajectoryFollower(id, vehicle, trajectory)
        return agent

    def createCogModAgent(self, id, vehicle, destinationPoint, driver_profile):
        agent = CogModAgent(id, vehicle, destinationPoint, driver_profile)
        return agent
