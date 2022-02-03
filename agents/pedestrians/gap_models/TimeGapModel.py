import carla
from abc import abstractmethod
from lib import NotImplementedInterface
from .GapModel import GapModel

class TimeGapModel(GapModel):

    @abstractmethod
    def getCriticalGap(self):
        raise NotImplementedInterface("getCriticalGap")

    @abstractmethod
    def getAvailableGap(self):
        raise NotImplementedInterface("getAvailableGap")

    @abstractmethod
    def getCriticalGap(self):
        raise NotImplementedInterface("getCriticalGap")

    @abstractmethod
    def getCriticalGap(self):
        raise NotImplementedInterface("getCriticalGap")
