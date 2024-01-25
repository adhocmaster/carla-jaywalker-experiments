from ..ForceModel import ForceModel
from abc import abstractmethod
from lib import NotImplementedInterface

class GapModel(ForceModel):

    @abstractmethod
    def canCross(self) -> bool:
        raise NotImplementedInterface("canCross")


    def calculateForce(self):
        return None

