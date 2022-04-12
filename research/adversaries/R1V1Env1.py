from lib.SimulationMode import SimulationMode
from .Environment import Environment
from ..ResearchFactory import ResearchFactory

class R1V1Env1(Environment):


    @staticmethod
    def create(host="127.0.0.1", port=2000):
        research = ResearchFactory.createResearch1v1(
            host=host, 
            port=port, 
            simulationMode=SimulationMode.SYNCHRONOUS, 
            stats=False
            )
        return R1V1Env1(
            research=research
        )
        
    def getActionTicks(self, action):
        """actionTime/time_delta"""

    def updateBehavior(self, action):
        self.logger.info("Updating behavior")
        # raise NotImplementedInterface("updateBehavior")

    def reward(self):
        # raise NotImplementedInterface("reward")
        return None


    def state(self):
        return None