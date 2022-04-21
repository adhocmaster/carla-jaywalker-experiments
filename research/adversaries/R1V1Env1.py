import logging
from math import ceil
from lib.SimulationMode import SimulationMode
from .Environment import Environment
from ..ResearchFactory import ResearchFactory

class R1V1Env1(Environment):


    @staticmethod
    def create(host="127.0.0.1", port=2000):
        research = ResearchFactory.createResearch1v1(
            host=host, 
            port=port, 
            defaultLogLevel=logging.WARNING,
            simulationMode=SimulationMode.SYNCHRONOUS, 
            stats=False
            )
        return R1V1Env1(
            research=research
        )
        
    def getActionTicks(self, action) -> int:
        """actionTime/time_delta"""
        actionTime = 1 # one second
        return int(max(actionTime // self.research.time_delta, 1))

        

    def updateBehavior(self, action):
        self.logger.warn("Updating behavior")
        # raise NotImplementedInterface("updateBehavior")

    def reward(self):
        # raise NotImplementedInterface("reward")
        return 100


    def state(self):
        return None