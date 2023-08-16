from agents.pedestrians.BehaviorType import BehaviorType
from agents.pedestrians.PedestrianAgent import PedestrianAgent
from agents.pedestrians.survival_models.EvasiveRetreatModel import EvasiveRetreatModel
from agents.pedestrians.survival_models.EvasiveStopModel import EvasiveStopModel
from agents.pedestrians.survival_models.SurvivalDestinationModel import SurvivalDestinationModel
from lib.LoggerFactory import LoggerFactory


class DynamicBehaviorModelFactory:

    def __init__(self) -> None:
        self.addMap = {
            BehaviorType.EVASIVE_RETREAT: self._addEvasiveRetreat,
            BehaviorType.EVASIVE_SPEEDUP: self._addEvasiveSpeedup,
            BehaviorType.EVASIVE_SLOWDOWN: self._addEvasiveSlowdown,
            BehaviorType.EVASIVE_SLOWDOWN_STOP: self._addEvasiveSlowdownStop,
            BehaviorType.EVASIVE_CROSS_BEHIND: self._addEvasiveCrossBehind,
            BehaviorType.EVASIVE_FLINCH: self._addEvasiveFlinch,
            BehaviorType.EVASIVE_STOP: self._addEvasiveStop,
            BehaviorType.IGNORE_ONCOMING: self._addIgnoreOncoming,

        }
        self.removeMap = {
            BehaviorType.EVASIVE_RETREAT: self._removeEvasiveRetreat,
            BehaviorType.EVASIVE_SPEEDUP: self._removeEvasiveSpeedup,
            BehaviorType.EVASIVE_SLOWDOWN: self._removeEvasiveSlowdown,
            BehaviorType.EVASIVE_SLOWDOWN_STOP: self._removeEvasiveSlowdownStop,
            BehaviorType.EVASIVE_CROSS_BEHIND: self._removeEvasiveCrossBehind,
            BehaviorType.EVASIVE_FLINCH: self._removeEvasiveFlinch,
            BehaviorType.EVASIVE_STOP: self._removeEvasiveStop,
            BehaviorType.IGNORE_ONCOMING: self._removeIgnoreOncoming,

        }
        self.name = f"DynamicBehaviorModelFactory"
        self._logger = LoggerFactory.create(self.name)

    def addBehavior(self, agent: PedestrianAgent, behavior: BehaviorType):
        if behavior in agent.currentBehaviors:
            return
        
        # remove conflicting behaviors first
        # if behavior == BehaviorType.EVASIVE_RETREAT:
        #     self.removeBehavior(agent, BehaviorType.EVASIVE_STOP)
        # elif behavior == BehaviorType.EVASIVE_STOP:
        #     self.removeBehavior(agent, BehaviorType.EVASIVE_RETREAT)

        agent.currentBehaviors.add(behavior)
        self.__addModel(agent, behavior)
        pass
    

    def removeBehavior(self, agent: PedestrianAgent, behavior: BehaviorType):
        if behavior not in agent.currentBehaviors:
            return
        self.__removeModel(agent, behavior)
        agent.currentBehaviors.remove(behavior)
        pass
    

    def __addModel(self, agent: PedestrianAgent, behavior: BehaviorType):
        handler = self.addMap.get(behavior)
        handler(agent)
        pass
    def __removeModel(self, agent: PedestrianAgent, behavior: BehaviorType):
        handler = self.removeMap.get(behavior)
        handler(agent)
        pass

    
    def _addEvasiveRetreat(self, agent: PedestrianAgent):

        self._logger.warning(f"Adding Evasive Retreat Model to {agent.id}")
        
        survivalDestModel = EvasiveRetreatModel(
                                agent, 
                                actorManager=agent.actorManager, obstacleManager=agent.obstacleManager, 
                                internalFactors=agent._localPlanner.internalFactors
                            )
        agent._localPlanner.modelMap[EvasiveRetreatModel] = survivalDestModel
        agent._localPlanner.models.append(survivalDestModel)
        agent._localPlanner.survivalModels.append(survivalDestModel)
        agent._localPlanner.stateTransitionModels.append(survivalDestModel)

        pass
    
    def _removeEvasiveRetreat(self, agent: PedestrianAgent):

        self._logger.warning(f"Removing Evasive Retreat Model from {agent.id}")
        agent._localPlanner.removeModel(EvasiveRetreatModel)

        pass
    
    def _addEvasiveSpeedup(self, agent: PedestrianAgent):
        self._logger.warning(f"Adding Evasive speedup Model to {agent.id}")
        pass
    
    def _removeEvasiveSpeedup(self, agent: PedestrianAgent):
        self._logger.warning(f"Removing Evasive speedup Model to {agent.id}")
        pass
    
    def _addEvasiveSlowdown(self, agent: PedestrianAgent):
        self._logger.warning(f"Adding Evasive slowdown Model to {agent.id}")
        pass

    def _removeEvasiveSlowdown(self, agent: PedestrianAgent):
        self._logger.warning(f"Removing Evasive slowdown Model to {agent.id}")
        pass

    def _addEvasiveSlowdownStop(self, agent: PedestrianAgent):
        self._logger.warning(f"Adding Evasive slowdownstop Model to {agent.id}")
        
        # add slowdown model
        # add stop model

        evasiveStopModel = EvasiveStopModel(
                                agent, 
                                actorManager=agent.actorManager, obstacleManager=agent.obstacleManager, 
                                internalFactors=agent._localPlanner.internalFactors
                            )
        
        agent._localPlanner.modelMap[EvasiveStopModel] = evasiveStopModel
        agent._localPlanner.models.append(evasiveStopModel)
        agent._localPlanner.survivalModels.append(evasiveStopModel)
        agent._localPlanner.stateTransitionModels.append(evasiveStopModel)

        pass
    
    def _removeEvasiveSlowdownStop(self, agent: PedestrianAgent):

        self._logger.warning(f"Removing Evasive slowdownstop Model from {agent.id}")
        agent._localPlanner.removeModel(EvasiveStopModel)

        pass

    def _addEvasiveCrossBehind(self, agent: PedestrianAgent):
        self._logger.warning(f"Adding Evasive crossbehind Model to {agent.id}")
        pass

    def _removeEvasiveCrossBehind(self, agent: PedestrianAgent):
        self._logger.warning(f"Removing Evasive crossbehind Model to {agent.id}")
        pass

    def _addEvasiveFlinch(self, agent: PedestrianAgent):
        self._logger.warning(f"Adding Evasive flinch Model to {agent.id}")
        pass

    def _removeEvasiveFlinch(self, agent: PedestrianAgent):
        self._logger.warning(f"Removing Evasive crossbehind Model to {agent.id}")
        pass

    def _addEvasiveStop(self, agent: PedestrianAgent):
        self._logger.warning(f"Adding Evasive stop Model to {agent.id}")
        # add stop model

        evasiveStopModel = EvasiveStopModel(
                                agent, 
                                actorManager=agent.actorManager, obstacleManager=agent.obstacleManager, 
                                internalFactors=agent._localPlanner.internalFactors
                            )
        
        agent._localPlanner.modelMap[EvasiveStopModel] = evasiveStopModel
        agent._localPlanner.models.append(evasiveStopModel)
        agent._localPlanner.survivalModels.append(evasiveStopModel)
        agent._localPlanner.stateTransitionModels.append(evasiveStopModel)
        
        pass

    def _removeEvasiveStop(self, agent: PedestrianAgent):

        self._logger.warning(f"Removing Evasive stop Model from {agent.id}")
        agent._localPlanner.removeModel(EvasiveStopModel)

        pass

    def _addIgnoreOncoming(self, agent: PedestrianAgent):
        self._logger.warning(f"Adding ignore oncoming Model to {agent.id}")
        pass

    def _removeIgnoreOncoming(self, agent: PedestrianAgent):
        self._logger.warning(f"Removing ignore oncoming Model to {agent.id}")
        pass

    pass