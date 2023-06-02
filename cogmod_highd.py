import logging
from lib import SimulationMode

from lib.MapManager import MapNames
from research import ResearchFactory


def ResearchCogMod():

    max_ticks = 10000
    host = "127.0.0.1"
    port = 2000
    timeout=10

    defaultLogLevel = logging.INFO
    outputDir = "logs"
    simulationMode = SimulationMode.SYNCHRONOUS

    scenario_id = 'scenario4'

    research = ResearchFactory.createResearchCogModHighD(maxTicks=max_ticks,
                                                        host=host,
                                                        port=port,
                                                        timeout=10.0,
                                                        defaultLogLevel=defaultLogLevel,
                                                        outputDir=outputDir,
                                                        simulationMode=simulationMode,
                                                        scenarioID=scenario_id)
    



if __name__ == '__main__':
    ResearchCogMod()