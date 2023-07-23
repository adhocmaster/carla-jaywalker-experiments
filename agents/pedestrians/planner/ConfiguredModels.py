from dataclasses import dataclass, field
from typing import List

from agents.pedestrians.DestinationModel import DestinationModel
from agents.pedestrians.ForceModel import ForceModel
from agents.pedestrians.StopGoModel import StopGoModel
from agents.pedestrians.factors.CrossingOncomingFactorModel import CrossingOncomingFactorModel

@dataclass
class ConfiguredModels:
    models: List[ForceModel] = field(default_factory=list)
    stateTransitionModels: List[ForceModel] = field(default_factory=list)
    crossingFactorModels: List[ForceModel] = field(default_factory=list)
    freezingModels: List[ForceModel] = field(default_factory=list)

    destinationModel: DestinationModel = None
    stopGoModel: StopGoModel = None
    crossingOncomingFactorModel: CrossingOncomingFactorModel = None

