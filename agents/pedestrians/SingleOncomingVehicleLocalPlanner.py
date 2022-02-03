import carla
from agents.pedestrians.PedState import PedState
from agents.pedestrians.StopGoModel import StopGoModel
from agents.pedestrians.factors import InternalFactors
from lib import Utils
from .PedestrianAgent import PedestrianAgent
from .PedestrianPlanner import PedestrianPlanner
from .DestinationModel import DestinationModel
from .gap_models.DistanceGapModel import DistanceGapModel
from .StateTransitionManager import StateTransitionManager
from lib import ActorManager, ObstacleManager, LoggerFactory, TooManyNewStates

class SingleOncomingVehicleLocalPlanner(PedestrianPlanner):


    def __init__(self, 
                    agent: PedestrianAgent, 
                    actorManager: ActorManager, obstacleManager: ObstacleManager,
                    internalFactors: InternalFactors
                    ) -> None:

        self.name = f"SingleOncomingVehicleLocalPlanner {agent.id}"
        self._logger = LoggerFactory.create(self.name)
        super().__init__(agent, actorManager=actorManager, obstacleManager=obstacleManager, internalFactors=internalFactors)
        # self._vehicle = vehicle
        self.models = []
        self.stateTransitionModels = []
        self.initModels()
        pass

    def initModels(self):
        self.destinationModel = DestinationModel(self.agent, actorManager=self.actorManager, obstacleManager=self.obstacleManager, internalFactors=self.internalFactors)
        pedGapModel = DistanceGapModel(self.agent, actorManager=self.actorManager, obstacleManager=self.obstacleManager, internalFactors=self.internalFactors)
        self.stopGoModel = StopGoModel(pedGapModel, self.agent, actorManager=self.actorManager, obstacleManager=self.obstacleManager, internalFactors=self.internalFactors)

        self.models = [self.destinationModel, self.stopGoModel]
        self.stateTransitionModels = [self.stopGoModel]

    
    # @property
    # def vehicle(self):
    #     return self._vehicle
    
    @property
    def logger(self):
        return self._logger

    # def setVehicle(self, vehicle: carla.Vehicle) -> None:
        # self._vehicle = vehicle
        # pass

    def setDestination(self, destination: carla.Location):
        super().setDestination(destination)
        self.destinationModel.setFinalDestination(destination)


    def calculateNextPedestrianState(self):
        newStates = set()
        for model in self.stateTransitionModels:
            newState = model.getNewState()
            if newState is not None:
                newStates.add(newState)
        
        if len(newStates) > 1:
            states = [state.value for state in newStates]
            self.logger.error(states)
            raise TooManyNewStates("Models returned different states")
        
        if len(newStates) > 0:
            return newStates.pop()

        return None
        # raise Exception("calculateNextPedestrianState")

    def transitionStateIfNeeded(self):
        self.logger.info(f"transitionStateIfNeeded")
        if self.done():
            self.logger.warn(f"changing agent state to finished")
            StateTransitionManager.changeAgentState(self.name, self.agent, PedState.FINISHED)
            return

        self.logger.warn(f"changing agent state from models")
        newState = self.calculateNextPedestrianState()
        if newState is not None:
            StateTransitionManager.changeAgentState(self.name, self.agent, newState)


    def calculateNextControl(self):
        
        # All the state transition should be contained here.

        self.logger.info(f"calculateNextControl")
        # StateTransitionManager.changeAgentState(self.name, self.agent, PedState.WAITING) # may also be frozen or other states which we will need to extend later.
        self.transitionStateIfNeeded()

        # if self.stopGoModel.canCross():
        #     StateTransitionManager.changeAgentState(self.name, self.agent, PedState.CROSSING)
        #     control = self.getNewControl()

        if self.agent.isFinished():
            self.logger.info(f"Finished. no new control")
            return self.getStopControl()

        if self.agent.isCrossing():
            control = self.getNewControl()
        else:
            self.logger.info(f"cannot cross due gap model")
            control = self.getStopControl()

        self.logger.info(f"New speed is {control.speed}")

        return control

    def getResultantForce(self):
        destForce = self.destinationModel.calculateForce()
        onComingVehicleForce = self.stopGoModel.calculateForce()
        self.logger.info(f"Force from destination model {destForce}")
        self.logger.info(f"Force from ped gap model {onComingVehicleForce}")
        return destForce + onComingVehicleForce

    # def getOncomingVehicles(self):
    #     if self.vehicle is None:
    #         return []
    #     return [self.vehicle]


    def getOncomingPedestrians(self):
        raise Exception("getOncomingPedestrians")

        
    def getPrecedingPedestrians(self):
        raise Exception("getPrecedingPedestrians")


    def getFollowingPedestrians(self):
        raise Exception("getFollowingPedestrians")