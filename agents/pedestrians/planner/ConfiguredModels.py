from dataclasses import dataclass, field
import logging
from typing import List

from agents.pedestrians.ForceModel import ForceModel
from agents.pedestrians.StateTransitionModel import StateTransitionModel
from agents.pedestrians.factors.CrossingFactorModel import CrossingFactorModel
from agents.pedestrians.survival_models.SurvivalModel import SurvivalModel

@dataclass
class ConfiguredModels:
    modelMap: dict = field(default_factory=dict) # TODO ModelFactory must use it
    models: List[ForceModel] = field(default_factory=list)
    stateTransitionModels: List[StateTransitionModel] = field(default_factory=list)
    crossingFactorModels: List[CrossingFactorModel] = field(default_factory=list)
    survivalModels: List[SurvivalModel] = field(default_factory=list)
    freezingModels: List[ForceModel] = field(default_factory=list)

    destinationModel = None
    stopGoModel = None
    crossingOncomingFactorModel = None

    def remove(self, name: any):
        """_summary_

        Args:
            name (any): class type
        """
        
        try:
            model = self.modelMap[name]

            self.models.remove(model)
            if isinstance(model, StateTransitionModel):
                self.stateTransitionModels.remove(model)
            if isinstance(model, CrossingFactorModel):
                self.crossingFactorModels.remove(model)
            if isinstance(model, SurvivalModel):
                self.survivalModels.remove(model)

            del self.modelMap[name]
            
            self.freezingModels.remove(model)
        except:
            logging.info(f"cannot remove non existing model {name}")

