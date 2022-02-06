
from typing import List
from .PedestrianPlanner import PedestrianPlanner
from ..PedestrianAgent import PedestrianAgent
from lib import ActorManager, ObstacleManager, LoggerFactory, TooManyNewStates
from agents.pedestrians.factors import *
from ..DestinationModel import DestinationModel
from ..gap_models import *
from agents.pedestrians.StopGoModel import StopGoModel
from ..factors.CrossingOncomingFactorModel import CrossingOncomingFactorModel

class ModelFactory:

    def __init__(self, 
                    planner: PedestrianPlanner,
                    agent: PedestrianAgent, 
                    actorManager: ActorManager, obstacleManager: ObstacleManager,
                    internalFactors: InternalFactors,  
                ) -> None:
        
        self.planner = planner
        self.agent = agent
        self.actorManager = actorManager
        self.obstacleManager = obstacleManager
        self.internalFactors = internalFactors

        self.name = f"ModelFactory {agent.id}"
        self._logger = LoggerFactory.create(self.name)
        pass


    def createRequiredModels(self):
        
        self.planner.destinationModel = DestinationModel(
                                    self.agent, 
                                    actorManager=self.actorManager, obstacleManager=self.obstacleManager, 
                                    internalFactors=self.internalFactors
                                    )
        # pedGapModel = DistanceGapModel(self.agent, actorManager=self.actorManager, obstacleManager=self.obstacleManager, internalFactors=self.internalFactors)
        pedGapModel = BrewerGapModel(
                                    self.agent, 
                                    actorManager=self.actorManager, obstacleManager=self.obstacleManager, 
                                    internalFactors=self.internalFactors
                                    )
        self.planner.stopGoModel = StopGoModel(         
                                    pedGapModel,
                                    self.agent, 
                                    actorManager=self.actorManager, obstacleManager=self.obstacleManager, 
                                    internalFactors=self.internalFactors
                                    )
        # factor models


        self.planner.models = [
                        self.planner.destinationModel, 
                        self.planner.stopGoModel
                      ]
        self.planner.stateTransitionModels = [self.planner.stopGoModel]


    def createOptionalModels(self, optionalFactors: List[Factors]):

        self.createCrossingModels(optionalFactors)


    def createCrossingModels(self, optionalFactors: List[Factors]):
        self.createCrossingOncomingVehicleModel(optionalFactors)


    def createCrossingOncomingVehicleModel(self, optionalFactors: List[Factors]):
        
        if Factors.CROSSING_ON_COMING_VEHICLE in optionalFactors:
            self.planner.crossingOncomingVehicleModel = CrossingOncomingFactorModel(
                                        self.agent, 
                                        actorManager=self.actorManager, obstacleManager=self.obstacleManager, 
                                        internalFactors=self.internalFactors
                                        )
            self.planner.models.append(self.planner.crossingOncomingVehicleModel)
            self.planner.crossingFactorModels.append(self.planner.crossingOncomingVehicleModel)