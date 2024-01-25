from enum import Enum

class Direction(Enum):
    
    """
    Enum for the lane position of a pedestrian. from the perspective of the ego vehicle.
    """
    LR = "LR"
    RL = "RL"