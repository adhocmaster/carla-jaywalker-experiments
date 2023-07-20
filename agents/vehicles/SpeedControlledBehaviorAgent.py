from agents.navigation.behavior_agent import BehaviorAgent  # pylint: disable=import-error


class SpeedControlledBehaviorAgent(BehaviorAgent):

    def __init__(self, vehicle, behavior='normal', max_speed=20):
        super().__init__(vehicle=vehicle, behavior=behavior)
        self._behavior.max_speed = max_speed
