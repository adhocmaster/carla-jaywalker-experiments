import carla
import os
from lib import ClientUser, LoggerFactory

class Research(ClientUser):
    
    def __init__(self, name, client: carla.Client, logLevel, outputDir:str = "logs") -> None:
        super().__init__(client)
        logPath = os.path.join(outputDir, "name.log")
        self.logger = LoggerFactory.createBaseLogger(name, defaultLevel=logLevel, file=logPath)
        pass