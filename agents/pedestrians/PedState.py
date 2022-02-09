from enum import Enum

class PedState(Enum):
    CROSSING = "CROSSING"
    WAITING = "WAITING"
    FROZEN = "FROZEN"
    INITALIZING = "INITALIZING"
    FINISHED = "FINISHED"
    SURVIVAL = "SURVIVAL"