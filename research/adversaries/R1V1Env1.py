import logging
from math import ceil
from lib.SimulationMode import SimulationMode
from .Environment import Environment
from ..ResearchFactory import ResearchFactory
from gym.spaces import *

class R1V1Env1(Environment):


    @staticmethod
    def create(
        host="127.0.0.1", 
        port=2000,
        coordinateSystem='ped'):


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

    
    def __init__(self, 
        research: BaseResearch, 
        coordinateSystem='ped'
        ):

        self.coordinateSystem = coordinateSystem
        self._roadState = None
        super().__init__(research)


        
    def getActionTicks(self, action) -> int:
        """actionTime/time_delta"""
        actionTime = 1 # one second
        return int(max(actionTime // self.research.time_delta, 1))

        

    def updateBehavior(self, action):
        self.logger.warn("Updating behavior")
        # raise NotImplementedInterface("updateBehavior")

    def setObsActionSpaces(self):

        # observation space in a dictionary format using pedestrian coordinate system: 
        ## TG: 0.0, inf
        ## waypoint on the vehicle lane closest to ped:, -inf, inf
        ## source: -inf, inf
        ## dest: -inf, inf
        ## w_speed: 0, inf
        ## relaxation: 0.0, inf
        ## 

        nLanes = 4
        relaxLow = 0.1
        relaxHigh = 1
        speedLow = 0.05
        speedHigh = 4

        self.observation_space = spaces.Dict({
            "pedestrian": spaces.Dict({
                'position': spaces.Box(low=-100, high=100, shape=(2,)), # 0,0 when coordinate system is ped, should be under 100 meter when cs is wp.
                'source': spaces.Box(low=-100, high=100, shape=(2,)),
                'dest': spaces.Box(low=-100, high=100, shape=(2,)),
                'relaxation_time': spaces.Box(low=relaxLow, high=relaxHigh, shape=(1,)),
                'risk_level': spaces.Discrete(4),
                'velocity': spaces.Box(low=-speedHigh, high=speedHigh, shape=(2,)),
                # "lane": spaces.Discrete(nLanes, start=1)

            }),
            "vehicle": spaces.Dict({
                'position': spaces.Box(low=-np.inf, high=np.inf, shape=(2,)), 
                'velocity': spaces.Box(low=-150, high=150, shape=(2,)),
                # "lane": spaces.Discrete(nLanes, start=1)
            }),
            "road": spaces.Dict({
                "nLanes": spaces.Discrete(nLanes, start=1) # maximum 4 lanes
                # "positions": spaces.Box(low=-100, high=100, shape=(nLanes, 2)) # x,y of the centerline for each lane from cs origin
            })
        })

        self.action_space = spaces.Box(
            low=[relaxLow, speedLow], 
            high=[relaxHigh, speedHigh]
        )



    def reward(self):
        # raise NotImplementedInterface("reward")
        return 100

    def roadState(self): 

        if self._roadState is None:
            self._roadState = {
                "nLanes" = 2,
                # "positions": spaces.Box(low=-100, high=100, shape=(nLanes, 2)) # x,y of the centerline for each lane from cs origin
            }

        return self._roadState

    
    def vehicleState(self):
        absPosition = self.research.vehicleAgent.position
        


    def state(self):
        walkerAgent = self.research.walkerAgent
        vehicleAgent = self.research.vehicleAgent

        state = {
            "pedestrian": {
                
                'position': np.array([0.0, 0.0]),
                'source': np.array([self.research.walkerSpawnPoint.location.x, self.research.walkerSpawnPoint.location.y]),
                'dest': np.array([self.research.walkerDestination.x, self.research.walkerDestination.y]),
                'relaxation_time': walkerAgent.getInternalFactor('relaxation_time'),
                'risk_level': walkerAgent.getInternalFactor('risk_level'),
                'velocity': np.array([walkerAgent.velocity.x, walkerAgent.velocity.y]),
                # "lane": spaces.Discrete(nLanes, start=1)
            }
            "vehicle": spaces.Dict({
                'position': spaces.Box(low=-np.inf, high=np.inf, shape=(2,)), 
                'velocity': spaces.Box(low=-150, high=150, shape=(2,)),
                # "lane": spaces.Discrete(nLanes, start=1)
            }),
            "road": self.roadState()
        }

