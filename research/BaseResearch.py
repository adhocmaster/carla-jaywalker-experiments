import carla
import os
from lib import ClientUser, LoggerFactory, MapManager, MapNames, SimulationVisualization

class BaseResearch(ClientUser):
    def __init__(self, name, client: carla.Client, logLevel, outputDir:str = "logs") -> None:
        super().__init__(client)
        logPath = os.path.join(outputDir, f"{name}.log")
        self.logger = LoggerFactory.getBaseLogger(name, defaultLevel=logLevel, file=logPath)

        self.mapManager = MapManager(client)
        self.mapManager.load(MapNames.circle_t_junctions)
        self.time_delta = 0.007

        self.visualizer = SimulationVisualization(self.client, self.mapManager)

        self.initWorldSettings()
        self.initVisualizer()

        pass


    def initWorldSettings(self):
        settings = self.world.get_settings()
        settings.substepping = False
        settings.fixed_delta_seconds = self.time_delta
        self.world.apply_settings(settings)
        pass

    
    def initVisualizer(self):
        self.visualizer.drawSpawnPoints()
        self.visualizer.drawSpectatorPoint()
        # self.visualizer.drawAllWaypoints(life_time=1.0)
        pass

    