from ..ForceModel import ForceModel
from abc import abstractmethod
from lib import NotImplementedInterface

class GapModel(ForceModel):

    @abstractmethod
    def canCross(self):
        raise NotImplementedInterface("canCross")



