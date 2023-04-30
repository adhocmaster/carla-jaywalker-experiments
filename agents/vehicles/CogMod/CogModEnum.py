from enum import Enum


class ManeuverType(Enum):
    LANEFOLLOW = 1
    VEHICLE_FOLLOW = 2
    LANECHANGE_LEFT = 3
    LANECHANGE_RIGHT = 4


class RequestType(Enum):
    MEMORY_ACCESS = 1
    MOTOR_CONTROL = 2
    COGNITIVE_PROCESS = 3


class ServerType(Enum):
    MOTOR_CONTROL = 1
    COMPLEX_COGNITION = 2
    LONGTERM_MEMORY = 3
    pass


class SubtaskState(Enum):
    """
    The state of the subtask.
    """
    ACTIVE = 0
    HALT = 1

    pass

class SubtaskType(Enum):
    LANEKEEPING = 0
    LANEFOLLOWING = 1
    HAZARD_DETECTION = 2
    INTERSECTION_CROSSING = 3
    REQULATORY = 4
    pass


class GazeDirection(Enum):
    """
    The gaze direction.
    """
    LEFTBLINDSPOT = 0       # 0.04
    LEFTMIRROR = 1          # 0.08
    LEFT = 2                # 0.1
    CENTER = 3              # 0.5
    RIGHT = 4               # 0.1
    RIGHTMIRROR = 5         # 0.08
    RIGHTBLINDSPOT = 6      # 0.04
    
    
    BACK = 7                # 0.06
    pass