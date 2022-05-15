import logging
import carla
import os

from lib import ClientUser, LoggerFactory, MapManager, MapNames, SimulationVisualization, Utils, SimulationMode
from research import *
# from research.SimulationMode import SimulationMode
from research.ResearchCogMod import ResearchCogMod

class ResearchFactory:
    def __init__(self, host="127.0.0.1", port=2000, output_dir="logs", map=MapNames.circle_t_junctions) -> None:
        self.map = map
        self.host = host
        self.port = int(port)
        self.output_dir = output_dir
        pass

    @staticmethod
    def createResearch1v1(
                            maxTicks=100, 
                            host="127.0.0.1", 
                            port=2000, 
                            defaultLogLevel=logging.INFO, 
                            output_dir="logs", 
                            map=MapNames.circle_t_junctions,
                            simulationMode = SimulationMode.ASYNCHRONOUS,
                            settingsId = "setting1",
                            stats=True
                            ) -> Research1v1:

        print(f"research chosen : R1v1 with host: {host}, port: {port}, log level: {defaultLogLevel}, output directory: {output_dir}")
        port = int(port)
        name = "Research1v1"
        logPath = os.path.join(output_dir, f"{name}.log")
        logger = LoggerFactory.getBaseLogger(name, defaultLevel=defaultLogLevel, file=logPath)
        client = Utils.createClient(logger, host, port)
        research = Research1v1(client, 
                         mapName=map, 
                         logLevel=defaultLogLevel, 
                         outputDir=output_dir,
                         simulationMode=simulationMode, 
                         settingsId=settingsId,
                         stats=stats
                         )
        # research.run(maxTicks=maxTicks)

        return research
    
    @staticmethod
    def createResearchCogMod(maxTicks=100, 
                             host="127.0.0.1", 
                             port=2000, 
                             defaultLogLevel=logging.INFO, 
                             output_dir="logs", 
                             map=MapNames.straight_road_with_parking, 
                             simulationMode=SimulationMode.ASYNCHRONOUS,
                             simulation_id='setting1'):

        print(f"research chosen : CogMod with host: {host}, port: {port}, log level: {defaultLogLevel}, output directory: {output_dir}")
        port = int(port)
        name = "ResearchCogMod"
        logPath = os.path.join(output_dir, f"{name}.log")
        logger = LoggerFactory.getBaseLogger(name, defaultLevel=defaultLogLevel, file=logPath)
        client = Utils.createClient(logger, host, port)
        research = ResearchCogMod(client, defaultLogLevel, map, output_dir, simulationMode, simulation_id)
        research.run(maxTicks=maxTicks)
