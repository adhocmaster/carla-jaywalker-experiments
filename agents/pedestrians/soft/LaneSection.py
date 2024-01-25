from enum import Enum

class LaneSection(Enum):
    """
    Enum for the lane position of a pedestrian. from the perspective of the ego vehicle.
    """
    LEFT = "LEFT"
    MIDDLE = "MIDDLE"
    RIGHT = "RIGHT"