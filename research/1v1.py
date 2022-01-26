import carla

from .research import Research

class Research1v1(Research):
    
    def __init__(self, args, client: carla.Client, logLevel, outputDir:str = "logs") -> None:
        