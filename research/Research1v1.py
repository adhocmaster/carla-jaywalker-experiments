import carla
import logging

from .BaseResearch import BaseResearch
from settings.circular_t_junction_settings import circular_t_junction_settings
from settings import SettingsManager
from agents.pedestrians import PedestrianFactory
from lib import Simulator

class Research1v1(BaseResearch):
    
    def __init__(self, client: carla.Client, logLevel, outputDir:str = "logs") -> None:
        self.name = "Research1v1"
        super().__init__(name=self.name, client=client, logLevel=logLevel, outputDir=outputDir)

        self.settingsManager = SettingsManager(self.client, circular_t_junction_settings)
        self.pedFactory = PedestrianFactory(self.world, visualizer=self.visualizer)

        self.setup()


    def destoryActors(self):
        self.logger.info('\ndestroying  walkers')
        self.walker.destroy()

    def setup(self):
        self.settingsManager.load("setting1")
        self.walkerSetting = self.getWalkerSetting()
        self.walkerSpawnPoint = carla.Transform(location = self.walkerSetting.source)
        self.walkerDestination = self.walkerSetting.destination
        self.walker = None
        self.walkerAgent = None

    
    def getWalkerSetting(self):
        walkerSettings = self.settingsManager.getWalkerSettings()
        walkerSetting = walkerSettings[1]
        return walkerSetting


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

        self.walkerAgent = self.pedFactory.createAgent(walker=self.walker, logLevel=logging.DEBUG)

        # exit(0)

        self.walkerAgent.set_destination(self.walkerDestination)
        self.visualizer.drawDestinationPoint(self.walkerDestination)

    #region simulation
    def run(self, maxTicks=1000):

        self.createWalker()

        onTickers = [self.visualizer.onTick, self.onTick]
        onEnders = [self.onEnd]
        simulator = Simulator(self.client, onTickers=onTickers, onEnders=onEnders)

        simulator.run(maxTicks)

    
    def onEnd(self):
        self.destoryActors()

    def onTick(self, world_snapshot):
        self.updateWalker(world_snapshot)
        self.updateVehicle(world_snapshot)
    
    
    def updateWalker(self, world_snapshot):

        if self.walkerAgent.done():
            print(f"Walker {self.walkerAgent.walker.id} reached destination. Going back")
            # if walkerAgent.destination == walkerSetting.destination:
            #     walkerAgent.set_destination(walkerSetting.source)
            #     visualizer.drawDestinationPoint(destination)
            # else:
            #     walkerAgent.set_destination(walkerSetting.destination)
            #     visualizer.drawDestinationPoint(destination)
            return

        if self.walkerAgent.canUpdate():
            control = self.walkerAgent.calculateControl()
            self.walker.apply_control(control)
            
    def updateVehicle(self, world_snapshot):
        pass

