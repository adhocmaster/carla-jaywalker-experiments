import carla
import math


class InteractionUtils:

    @staticmethod
    def isOncoming(me: carla.Actor, other: carla.Actor) -> bool:
        otherVelo = other.get_velocity()
        if otherVelo.length() < 0.0001:
            return False
        
        locationVec = me.get_location() - other.get_location()
        return otherVelo.dot(locationVec) > 0