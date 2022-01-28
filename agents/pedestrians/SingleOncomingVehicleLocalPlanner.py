import carla
from lib import Utils
from .PedestrianPlanner import PedestrianPlanner
from .DestinationModel import DestinationModel
from lib import ActorManager, ObstacleManager, LoggerFactory

class SingleOncomingVehicleLocalPlanner(PedestrianPlanner):


    def __init__(self, 
                    agent, 
                    vehicle: carla.Vehicle = None
                    ) -> None:

        self.logger = LoggerFactory.create("SingleOncomingVehicleLocalPlanner")
        super().__init__(agent)
        self._vehicle = vehicle
        self.initModels()
        pass

    def initModels(self):
        self.destinationModel = DestinationModel(self.agent, actorManager=self.actorManager, obstacleManager=self.obstacleManager)

    
    @property
    def vehicle(self):
        return self._vehicle

    def setVehicle(self, vehicle: carla.Vehicle) -> None:
        self._vehicle = vehicle
        pass

    def setDestination(self, destination: carla.Location):
        super().setDestination(destination)
        self.destinationModel.setFinalDestination(destination)


    def calculateNextPedestrianState(self):
        raise Exception("calculateNextPedestrianState")

    def calculateNextControl(self):
        
        direction = self.destinationModel.getDesiredDirection()
        
        speed = self.destinationModel.getDesiredSpeed()

        
        self.logger.info(f"Calculating control - Distance to destination is {self.getDistanceToDestination()} meters, next speed: {speed} direction: {direction}")
        # self.logger.info(f"Calculating control - Distance to destination is  next speed: {speed} direction: {direction}")

        control = carla.WalkerControl(
            direction = direction,
            speed = speed,
            jump = False
        )

        return control


    def getOncomingVehicles(self):
        if self.vehicle is None:
            return []
        return [self.vehicle]


    def getOncomingPedestrians(self):
        raise Exception("getOncomingPedestrians")

        
    def getPrecedingPedestrians(self):
        raise Exception("getPrecedingPedestrians")


    def getFollowingPedestrians(self):
        raise Exception("getFollowingPedestrians")