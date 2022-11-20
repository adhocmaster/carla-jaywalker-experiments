from enum import Enum, auto

class Factors(Enum):
    CROSSING_ON_COMING_VEHICLE = "CROSSING_ON_COMING_VEHICLE"
    SURVIVAL_DESTINATION = "SURVIVAL_DESTINATION"
    FREEZING_FACTOR = "FREEZING_FACTOR"
    MAGNETIC_VEHICLE = "MAGNETIC_VEHICLE"
    DRUNKEN_WALKER = "DRUNKEN_WALKER"
    ANTISURVIVAL = "ANTISURVIVAL"
    # CROSSWALK_MODEL = auto()

    @staticmethod
    def getByValue(factor: str) -> Factors:

        factor = factor.strip().upper()

        if factor == Factors.CROSSING_ON_COMING_VEHICLE.value:
            return Factors.CROSSING_ON_COMING_VEHICLE

        if factor == Factors.SURVIVAL_DESTINATION.value:
            return Factors.SURVIVAL_DESTINATION

        if factor == Factors.FREEZING_FACTOR.value:
            return Factors.FREEZING_FACTOR

        if factor == Factors.MAGNETIC_VEHICLE.value:
            return Factors.MAGNETIC_VEHICLE

        if factor == Factors.DRUNKEN_WALKER.value:
            return Factors.DRUNKEN_WALKER

        if factor == Factors.ANTISURVIVAL.value:
            return Factors.ANTISURVIVAL

    