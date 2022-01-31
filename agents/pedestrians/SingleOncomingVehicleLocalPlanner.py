import carla
from agents.pedestrians.PedState import PedState
from lib import Utils
from .PedestrianAgent import PedestrianAgent
from .PedestrianPlanner import PedestrianPlanner
from .DestinationModel import DestinationModel
from .PedGapModel import PedGapModel
from .StateTransitionManager import StateTransitionManager
from lib import ActorManager, ObstacleManager, LoggerFactory

class SingleOncomingVehicleLocalPlanner(PedestrianPlanner):


    def __init__(self, 
                    agent: PedestrianAgent, 
                    vehicle: carla.Vehicle = None
                    ) -> None:

        self._logger = LoggerFactory.create("SingleOncomingVehicleLocalPlanner")
        super().__init__(agent)
        self._vehicle = vehicle
        self.initModels()
        pass

    def initModels(self):
        self.destinationModel = DestinationModel(self.agent, actorManager=self.actorManager, obstacleManager=self.obstacleManager)
        self.pedGapModel = PedGapModel(self.agent, actorManager=self.actorManager, obstacleManager=self.obstacleManager)

    
    @property
    def vehicle(self):
        return self._vehicle
    
    @property
    def logger(self):
        return self._logger

    def setVehicle(self, vehicle: carla.Vehicle) -> None:
        self._vehicle = vehicle
        pass

    def setDestination(self, destination: carla.Location):
        super().setDestination(destination)
        self.destinationModel.setFinalDestination(destination)


    def calculateNextPedestrianState(self):
        raise Exception("calculateNextPedestrianState")

    def calculateNextControl(self):
        
        # direction = self.destinationModel.getDesiredDirection()
        
        # speed = self.destinationModel.getDesiredSpeed()

        
        # self.logger.info(f"Calculating control - Distance to destination is {self.getDistanceToDestination()} meters, next speed: {speed} direction: {direction}")
        # # self.logger.info(f"Calculating control - Distance to destination is  next speed: {speed} direction: {direction}")

        # control = carla.WalkerControl(
        #     direction = direction,
        #     speed = speed,
        #     jump = False
        # )

        # Now we have force and we have time delta. So amount of change in velocity is time_delta * force + old velocity

        if self.pedGapModel.canCross():
            control = self.getNewControl()
            StateTransitionManager.changeAgentState("Planner", self.agent, PedState.CROSSING)
        else:

            self.logger.info(f"cannot cross due gap model")
            oldControl = self.agent.getOldControl()
            
            control = carla.WalkerControl(
                direction = oldControl.direction,
                speed = 0,
                jump = False
            )

        self.logger.info(f"New speed is {control.speed}")

        return control

    def getResultantForce(self):
        destForce = self.destinationModel.calculateForce()
        onComingVehicleForce = self.pedGapModel.calculateForce()
        self.logger.info(f"Force from destination model {destForce}")
        self.logger.info(f"Force from ped gap model {onComingVehicleForce}")
        return destForce + onComingVehicleForce

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