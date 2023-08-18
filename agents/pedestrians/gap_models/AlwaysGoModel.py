
from .GapModel import GapModel
import numpy as np

class AlwaysGoModel(GapModel):
    
    def canCross(self) -> bool:
        return True