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
        self.tm.global_percentage_speed_difference(-20)

        
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

    
    def batchSpawn(self, spawnPoints: carla.Transform, autoPilot=True):

        batch = []
        for spawnPoint in spawnPoints:
            if spawnPoint.location.z < 0.5:
                spawnPoint.location.z = 0.5 
                
            vehicleBp = self.create()

            if autoPilot:
                batch.append(
                    carla.command.SpawnActor(vehicleBp, spawnPoint)
                        .then(carla.command.SetAutopilot(carla.command.FutureActor, True, self.tm.get_port()))
                )
            else:
                batch.append(
                    carla.command.SpawnActor(vehicleBp, spawnPoint)
                )

        
        generatedVehicles = []

        for response in self.client.apply_batch_sync(batch):
            if response.error:
                logging.error(response.error)
            else:
                vehicle = self.world.get_actor(response.actor_id)
                generatedVehicles.append(vehicle)
                self.vehicles.extend(generatedVehicles)

                self.tm.auto_lane_change(vehicle, random.choice([True, False]))
                self.tm.ignore_lights_percentage(vehicle, 20)
                self.tm.ignore_signs_percentage(vehicle, 20)
                self.tm.ignore_vehicles_percentage(vehicle, 20)
                self.tm.ignore_walkers_percentage(vehicle, 20)


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
