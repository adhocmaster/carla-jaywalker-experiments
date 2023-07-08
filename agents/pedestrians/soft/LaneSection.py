from enum import Enum

class LaneSection(Enum):
    """
    Enum for the lane position of a pedestrian.
    """
    LEFT = "LEFT"
    MIDDLE = "MIDDLE"
    RIGHT = "RIGHT"