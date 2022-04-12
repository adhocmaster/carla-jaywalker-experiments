from abc import abstractmethod
import carla
import os
from lib import ClientUser, LoggerFactory, MapManager, MapNames, SimulationVisualization, NotImplementedInterface, SimulationMode
# from lib.SimulationMode import SimulationMode

class BaseResearch(ClientUser):
    def __init__(self, name, client: carla.Client, mapName, logLevel, outputDir:str = "logs", simulationMode = SimulationMode.ASYNCHRONOUS) -> None:
        super().__init__(client)

        self.name = name
        self.mapName = mapName
        self.logLevel = logLevel
        self.outputDir = outputDir

        logPath = os.path.join(outputDir, f"{name}.log")
        self.logger = LoggerFactory.getBaseLogger(name, defaultLevel=logLevel, file=logPath)

        self.simulationMode = simulationMode

        self.time_delta = None
        self.mapManager = None
        self.visualizer = None


        self.initWorldSettings()
        self.initVisualizer()

        pass


    def configureMap(self):
        self.mapManager = MapManager(self.client)
        self.mapManager.load(self.mapName)

    def reset(self):
        self.client.reload_world(False)


    def initWorldSettings(self):
        # settings = self.world.get_settings()
        # settings.substepping = False
        # settings.fixed_delta_seconds = self.time_delta
        # self.world.apply_settings(settings)
        
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.initWorldSettingsAsynchronousMode()
        else:
            self.initWorldSettingsSynchronousMode()

        pass

    
    def initVisualizer(self):
        self.visualizer = SimulationVisualization(self.client, self.mapManager)
        self.visualizer.drawSpawnPoints()
        self.visualizer.drawSpectatorPoint()
        # self.visualizer.drawAllWaypoints(life_time=1.0)
        pass

    def initWorldSettingsAsynchronousMode(self):
        self.configureMap()
        self.time_delta = 0.007
        settings = self.world.get_settings()
        settings.substepping = False
        settings.fixed_delta_seconds = self.time_delta
        self.world.apply_settings(settings)
        pass

    def initWorldSettingsSynchronousMode(self):
        self.time_delta = 0.05
        settings = self.world.get_settings()
        # settings.substepping = False # https://carla.readthedocs.io/en/latest/python_api/#carlaworldsettings
        settings.synchronous_mode = True # Enables synchronous mode
        settings.fixed_delta_seconds = self.time_delta # Sets fixed time step
        self.world.apply_settings(settings)
        self.configureMap()
        pass

    @abstractmethod
    def createDynamicAgents(self):
        raise NotImplementedInterface("createDynamicAgents")

    @abstractmethod
    def setupSimulator(self):
        raise NotImplementedInterface("setupSimulator")

    