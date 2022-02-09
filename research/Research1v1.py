import carla
import logging
import random

from .BaseResearch import BaseResearch
from settings.circular_t_junction_settings import circular_t_junction_settings
from settings import SettingsManager
from agents.pedestrians import PedestrianFactory
from agents.pedestrians.factors import Factors
from agents.vehicles import VehicleFactory
from lib import Simulator
from lib import Utils

class Research1v1(BaseResearch):
    
    def __init__(self, client: carla.Client, logLevel, outputDir:str = "logs") -> None:
        self.name = "Research1v1"
        super().__init__(name=self.name, client=client, logLevel=logLevel, outputDir=outputDir)

        self.settingsManager = SettingsManager(self.client, circular_t_junction_settings)
        self.pedFactory = PedestrianFactory(self.client, visualizer=self.visualizer, time_delta=self.time_delta)
        self.vehicleFactory = VehicleFactory(self.client, visualizer=self.visualizer)

        self.setup()


    def destoryActors(self):
        self.logger.info('\ndestroying  walkers')
        if self.walker is not None:
            self.walker.destroy()
        self.logger.info('\ndestroying  vehicles')
        self.vehicle.destroy()

    def setup(self):
        self.settingsManager.load("setting3")

        self.walker = None
        self.walkerAgent = None
        self.walkerSetting = self.getWalkerSetting()
        self.walkerSpawnPoint = carla.Transform(location = self.walkerSetting.source)
        self.walkerDestination = self.walkerSetting.destination

        self.vehicle = None
        self.vehicleAgent = None
        self.vehicleSetting = self.getVehicleSetting()
        self.vehicleSpawnPoint = self.settingsManager.locationToVehicleSpawnPoint(self.vehicleSetting.source)
        self.vehicleDestination = self.vehicleSetting.destination

        self.simulator = None # populated when run

    
    def getWalkerSetting(self):
        walkerSettings = self.settingsManager.getWalkerSettings()
        walkerSetting = walkerSettings[1]
        return walkerSetting

    def getVehicleSetting(self):
        vehicleSetting = self.settingsManager.getVehicleSettings()
        vehicleSetting = vehicleSetting[0]
        return vehicleSetting


    def createWalker(self):
        
        self.visualizer.drawWalkerNavigationPoints([self.walkerSpawnPoint])


        self.walker = self.pedFactory.spawn(self.walkerSpawnPoint)

        if self.walker is None:
            self.logger.error("Cannot spawn walker")
            exit("Cannot spawn walker")
        else:
            self.logger.info(f"successfully spawn walker {self.walker.id} at {self.walkerSpawnPoint.location.x, self.walkerSpawnPoint.location.y, self.walkerSpawnPoint.location.z}")
            self.logger.info(self.walker.get_control())
            
            # visualizer.trackOnTick(walker.id, {"life_time": 1})      
        
        self.world.wait_for_tick() # otherwise we can get wrong agent location!

        optionalFactors = [Factors.CROSSING_ON_COMING_VEHICLE]

        config = {
            "visualizationForceLocation": carla.Location(x=-150.0, y=2.0, z=1.5),
            "visualizationInfoLocation": carla.Location(x=-155.0, y=0.0, z=1.5)
        }

        self.walkerAgent = self.pedFactory.createAgent(walker=self.walker, logLevel=logging.DEBUG, optionalFactors=optionalFactors, config=config)

        self.walkerAgent.setDestination(self.walkerDestination)
        self.visualizer.drawDestinationPoint(self.walkerDestination)

        # attach actor manager

        pass

    
    def createVehicle(self):
        vehicleSpawnPoint = self.vehicleSpawnPoint
        # vehicleSpawnPoint = random.choice(self.mapManager.spawn_points)
        self.vehicle = self.vehicleFactory.spawn(vehicleSpawnPoint)       
        if self.vehicle is None:
            self.logger.error("Cannot spawn vehicle")
            exit("Cannot spawn vehicle")
        else:
            self.logger.info(f"successfully spawn vehicle at {vehicleSpawnPoint.location.x, vehicleSpawnPoint.location.y, vehicleSpawnPoint.location.z}")

        self.world.wait_for_tick() # otherwise we can get wrong vehicle location!

        # self.vehicleAgent = self.vehicleFactory.createAgent(self.vehicle, target_speed=20, logLevel=logging.DEBUG)
        self.vehicleAgent = self.vehicleFactory.createBehaviorAgent(self.vehicle, behavior='normal', logLevel=logging.DEBUG)

        spawnXYLocation = carla.Location(x=vehicleSpawnPoint.location.x, y=vehicleSpawnPoint.location.y, z=0.001)

        # destination = self.getNextDestination(spawnXYLocation)
        destination = self.vehicleSetting.destination

        self.vehicleAgent.set_destination(destination, start_location=spawnXYLocation)
        self.visualizer.drawDestinationPoint(destination)

        pass


    def getNextDestination(self, currentLocation):

        return carla.Location(x=-132.862671, y=3, z=0.0)

        destination = random.choice(self.mapManager.spawn_points).location
        count = 1
        while destination.distance(currentLocation) < 5:
            destination = random.choice(self.mapManager.spawn_points).location
            count += 1
            if count > 5:
                self.logger.error(f"Cannot find a destination from {currentLocation}")
                raise Exception("Cannot find a destination")
        return destination


    #region simulation
    def run(self, maxTicks=1000):

        # self.visualizer.drawPoint(carla.Location(x=-96.144363, y=-3.690280, z=1), color=(0, 0, 255), size=0.1)
        # self.visualizer.drawPoint(carla.Location(x=-134.862671, y=-42.092407, z=0.999020), color=(0, 0, 255), size=0.1)

        # return

        self.createWalker()
        self.createVehicle()

        self.world.wait_for_tick()

        onTickers = [self.visualizer.onTick, self.onTick, self.restart]
        onEnders = [self.onEnd]
        self.simulator = Simulator(self.client, onTickers=onTickers, onEnders=onEnders)

        self.simulator.run(maxTicks)

        # try: 
        # except Exception as e:
        #     self.logger.exception(e)


    def restart(self, world_snapshot):
        
        if self.walkerAgent.isFinished():
            # 1. recreated vehicle
            self.recreateVehicle()
            # 2. reset walker
            self.resetWalker(reverse=False)

    
    def recreateVehicle(self):
        # destroy current one
        # self.simulator.removeOnTicker()
        self.logger.warn(f"Recreating vehicle")
        self.vehicle.destroy()
        self.vehicleAgent = None
        self.vehicle = None
        self.createVehicle()

    def resetWalker(self, reverse=False):

        # default keeps the same start and end as the first episode
        source = self.walkerSetting.source
        newDest = self.walkerSetting.destination

        if reverse:
            source =  self.walkerAgent.destination
            if self.walkerAgent.destination == newDest: # get back to source
                newDest = source
                

        self.walkerAgent.reset()
        self.walkerAgent.setDestination(self.walkerSetting.source)
    
    def onEnd(self):
        self.destoryActors()

    def onTick(self, world_snapshot):

        self.walkerAgent.onTickStart(world_snapshot)

        self.updateWalker(world_snapshot)
        self.updateVehicle(world_snapshot)
    
    
    def updateWalker(self, world_snapshot):

        # print("updateWalker")

        if self.walkerAgent is None:
            self.logger.warn(f"No walker to update")
            return

        if self.walkerAgent.isFinished():
            print(f"Walker {self.walkerAgent.walker.id} reached destination. Going back")
            # if walkerAgent.destination == walkerSetting.destination:
            #     walkerAgent.set_destination(walkerSetting.source)
            #     visualizer.drawDestinationPoint(destination)
            # else:
            #     walkerAgent.set_destination(walkerSetting.destination)
            #     visualizer.drawDestinationPoint(destination)
            # return

        # print("canUpdate")
        # if self.walkerAgent.canUpdate():
        control = self.walkerAgent.calculateControl()
        # print("apply_control")
        self.walker.apply_control(control)
            
    def updateVehicle(self, world_snapshot):

        if self.vehicleAgent is None:
            self.logger.warn(f"No vehicle to update")
            return 

        if self.vehicleAgent.done():
            destination = random.choice(self.mapManager.spawn_points).location
            # self.vehicleAgent.set_destination(destination, self.vehicle.get_location())
            self.vehicleAgent.set_destination(destination)
            self.logger.info("The target has been reached, searching for another target")
            self.visualizer.drawDestinationPoint(destination)

        
        control = self.vehicleAgent.run_step()
        control.manual_gear_shift = False
        self.logger.info(control)
        self.vehicle.apply_control(control)
        pass

