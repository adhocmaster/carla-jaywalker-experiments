import carla
class SourceDestinationPair:

    def __init__(self, source: carla.Location, destination: carla.Location) -> None:
        self.source = source
        self.destination = destination
        pass

    def __str__(self) -> str:
        return (
            f"source: {self.source} "
            f"destination: {self.destination}"
        )
    
    def toDict(self):
        return {
            "source": (self.source.x, self.source.y),
            "destination": (self.destination.x, self.destination.y)
        }