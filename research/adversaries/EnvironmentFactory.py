import logging

from enum import Enum, auto
from .R1V1Env1 import R1V1Env1
from .R4V4EnvNavModel import R4V4EnvNavModel
from .R1V1Env1NavModel import R1V1Env1NavModel

class AvailableEnvironments(Enum):
    R1V1Env1 = R1V1Env1
    R1V1Env1NavModel = R1V1Env1NavModel
    R4V4EnvNavModel = R4V4EnvNavModel

class EnvironmentFactory:

    @staticmethod
    def create(
        envName: AvailableEnvironments, 
        host="127.0.0.1", 
        port=2000, 
        defaultLogLevel=logging.WARNING,
        output_dir="logs"
        ):
        return envName.value.create(
            host=host,
            port=port,
            defaultLogLevel=defaultLogLevel,
            output_dir=output_dir
        )