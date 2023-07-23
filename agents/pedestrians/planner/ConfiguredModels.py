from dataclasses import dataclass, field
from typing import List

from agents.pedestrians.ForceModel import ForceModel
from agents.pedestrians.StateTransitionModel import StateTransitionModel
from agents.pedestrians.factors.CrossingFactorModel import CrossingFactorModel
from agents.pedestrians.survival_models.SurvivalModel import SurvivalModel

@dataclass
class ConfiguredModels:
    models: List[ForceModel] = field(default_factory=list)
    stateTransitionModels: List[StateTransitionModel] = field(default_factory=list)
    crossingFactorModels: List[CrossingFactorModel] = field(default_factory=list)
    survivalModels: List[SurvivalModel] = field(default_factory=list)
    freezingModels: List[ForceModel] = field(default_factory=list)

    destinationModel = None
    stopGoModel = None
    crossingOncomingFactorModel = None

