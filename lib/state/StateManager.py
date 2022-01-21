
from ..OnTicker import OnTicker

class StateManager(OnTicker):

    def __init__(self, client, trafficParticipants=None, staticObjects=None):
        super().__init__(client)
        self.positionLastTick = {}

        self.trafficParticipants = []
        if trafficParticipants is not None:
            self.trafficParticipants = trafficParticipants

        self.staticObjects = []
        if staticObjects is not None:
            self.staticObjects = staticObjects
        for obj in self.trafficParticipants:
            self.positionLastTick[obj] = obj.get_location()
        

        self.allObjects = self.trafficParticipants + self.staticObjects



    def updatePositionLastTick(self):
        for tp in self.trafficParticipants:
            self.positionLastTick[tp] = tp.get_location()
    
    def onTick(self, world_snapshot):

        # for tp in self.trafficParticipants:
        #     print("Actor position:", tp.get_location())
        return super().onTick(world_snapshot)
        


    


    
