from abc import abstractmethod
from lib import NotImplementedInterface
from .ForceModel import ForceModel

class StateTransitionModel(ForceModel):

    @abstractmethod
    def getNewState(self):
        raise NotImplementedInterface("getNewState")