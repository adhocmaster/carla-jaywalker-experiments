
from agents.pedestrians.factors import InternalFactors
from .GapUtils import GapUtils
from .ProbabilisticModel import ProbabilisticModel

class BrewerGap(ProbabilisticModel):

    def __init__(self, internalFactors: InternalFactors) -> None:
        self.beta0 = internalFactors["brewer_beta0"]
        self.beta1 = internalFactors["brewer_beta1"]
        pass

    def p_go(self, gap):
        return 1 - self.p_stop(gap)

    def p_stop(self, gap):
        return GapUtils.sigmoid(gap)