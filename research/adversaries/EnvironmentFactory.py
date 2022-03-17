from numpy import swapaxes
from R1V1Env1 import R1V1Env1
from enum import Enum, auto

class AvailableEnvironments(Enum):
    R1V1Env1 = R1V1Env1

class EnvironmentFactory:

    @staticmethod
    def create(envName: AvailableEnvironments):
        