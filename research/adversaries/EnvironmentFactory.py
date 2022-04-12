from enum import Enum, auto
from .R1V1Env1 import R1V1Env1

class AvailableEnvironments(Enum):
    R1V1Env1 = R1V1Env1

class EnvironmentFactory:

    @staticmethod
    def create(envName: AvailableEnvironments, host="127.0.0.1", port=2000):
        return envName.value.create()