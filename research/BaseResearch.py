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
        # self.client.reload_world(False)
        self.mapManager.reload()


    def initWorldSettings(self):
        # settings = self.world.get_settings()
        # settings.substepping = False
        # settings.fixed_delta_seconds = self.time_delta
        # self.world.apply_settings(settings)
        
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.logger.warn(f"Starting simulation in asynchronous mode")
            self.initWorldSettingsAsynchronousMode()
        else:
            self.logger.warn(f"Starting simulation in synchronous mode")
            self.initWorldSettingsSynchronousMode()

        pass

    
    def initVisualizer(self):
        self.visualizer = SimulationVisualization(self.client, self.mapManager)
        self.visualizer.drawSpawnPoints(life_time=1.0)
        self.visualizer.drawSpectatorPoint()
        # self.visualizer.drawAllWaypoints(life_time=1.0)
        pass

    def initWorldSettingsAsynchronousMode(self):
        self.configureMap()
        self.time_delta = 0.007
        settings = self.world.get_settings()
        settings.synchronous_mode = False # Enables synchronous mode
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

    def tickOrWaitBeforeSimulation(self):
        """
        It will not call simulation events. Only purpose is for some intializations which needs to be applied before simulation runs, e.g., actor creation.
        """
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.world.wait_for_tick()
        else:
            self.world.tick()

    @abstractmethod
    def createDynamicAgents(self):
        raise NotImplementedInterface("createDynamicAgents")

    @abstractmethod
    def setupSimulator(self):
        raise NotImplementedInterface("setupSimulator")

    