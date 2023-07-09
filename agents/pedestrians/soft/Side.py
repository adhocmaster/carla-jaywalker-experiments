from enum import Enum

class Side(Enum):
    
    """
    Enum for the lane position of a pedestrian. from the perspective of the ego vehicle.
    """
    LEFT = "LEFT"
    SAME = "SAME"
    RIGHT = "RIGHT"