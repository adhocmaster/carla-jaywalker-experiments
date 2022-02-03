from abc import abstractmethod
from lib import NotImplementedInterface

class ProbabilisticModel:
    
    @abstractmethod
    def p_go(self, gap):
        raise NotImplementedInterface("p_go")

    @abstractmethod
    def p_stop(self, gap):
        raise NotImplementedInterface("p_stop")
