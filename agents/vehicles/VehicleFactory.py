import carla
import random
import logging


from agents.navigation.behavior_agent import BehaviorAgent  # pylint: disable=import-error
from agents.navigation.basic_agent import BasicAgent  # pylint: disable=import-error
from lib import LoggerFactory, ClientUser

from agents.vehicles.qnactr.CogMod import CogModAgent  # cogmod agent 
from .qnactr.TrajectoryFollower import TrajectoryFollower  # trajectory follower actor agent


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
        self.vehicleBps = self.bpLib.filter('vehicle.audi.*')

        
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

    
    def spawn(self, spawnPoint):
        vehicleBp = self.create()
        vehicle = self.world.spawn_actor(vehicleBp, spawnPoint)
        self.vehicles.append(vehicle)
        return vehicle

    
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
