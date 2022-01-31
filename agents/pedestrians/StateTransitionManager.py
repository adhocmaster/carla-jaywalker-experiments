from .PedState import PedState

class StateTransitionManager:

    @staticmethod
    def changeAgentState(whoIsChanging:str, agent: any, newState:PedState):
        agent.logger.info(f"{whoIsChanging} is changing agent {agent.id}'s state from {agent.state} to {newState}")
        agent.state = newState