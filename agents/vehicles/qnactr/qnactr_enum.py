from enum import Enum


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

