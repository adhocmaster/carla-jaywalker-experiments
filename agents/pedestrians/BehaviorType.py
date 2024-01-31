from enum import Enum

class BehaviorType(Enum):
    EVASIVE_STOP = "EVASIVE_STOP"
    EVASIVE_FLINCH = "EVASIVE_FLINCH"
    EVASIVE_RETREAT = "EVASIVE_RETREAT"
    EVASIVE_SPEEDUP = "EVASIVE_SPEEDUP"
    EVASIVE_SLOWDOWN = "EVASIVE_SLOWDOWN"
    EVASIVE_SLOWDOWN_STOP = "EVASIVE_SLOWDOWN_STOP"
    EVASIVE_CROSS_BEHIND = "EVASIVE_CROSS_BEHIND"
    IGNORE_ONCOMING = "IGNORE_ONCOMING"