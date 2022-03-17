from research.SimulationMode import SimulationMode
from .Environment import Environment
from ..ResearchFactory import ResearchFactory

class R1V1Env1(Environment):


    @staticmethod
    def create():
        research = ResearchFactory.createResearch1v1(stats=False, simulationMode=SimulationMode.SYNCHRONOUS)
        return R1V1Env1(
            research=research
        )

    def updateBehavior(self):
        self.logger.info("Updating behavior")
        # raise NotImplementedInterface("updateBehavior")

    def reward(self):
        # raise NotImplementedInterface("reward")
        return None

    # def isEpisodeDone(self):
    #     return False

    def state(self):
        return None