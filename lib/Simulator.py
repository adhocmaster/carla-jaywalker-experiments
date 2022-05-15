import eventlet
import time
from .ClientUser import ClientUser
from .LoggerFactory import LoggerFactory
import traceback

from .SimulationMode import SimulationMode

class Simulator(ClientUser):

    def __init__(self, client, onTickers=None, onEnders=None, useThreads=False, sleep=0.05, simulationMode=SimulationMode.ASYNCHRONOUS):
        self.name = "Simulator"
        self.logger = LoggerFactory.create(self.name)
        super().__init__(client)
        self.pool = eventlet.GreenPool()
        self.useThreads = useThreads
        self.sleep = sleep

        self.onTickers = [] # methods to call on tick
        if onTickers is not None:
            self.onTickers = onTickers
        self.onEnders = [] # methods to call on end
        if onEnders is not None:
            self.onEnders = onEnders

        self.simulationMode = simulationMode

    
    def addOnticker(self, onTicker):
        self.onTickers.append(onTicker)
    
    def removeOnTicker(self, onTicker):
        self.onTickers.remove(onTicker)

    def addOnEnder(self, onEnder):
        self.onEnders.append(onEnder)

    def removeOnEnder(self, onEnder):
        self.onEnders.remove(onEnder)

    

    def run(self, maxTicks):
        if self.useThreads:
            self.pool.spawn_n(self.loop, maxTicks)
        else:
            self.loop(maxTicks)

    
    def onEnd(self):
        for onEnder in self.onEnders:
            onEnder()
    
    def loop(self, maxTicks):

        try:
            for i in range(maxTicks):
                self.tick(i)
                time.sleep(self.sleep)
                
        except Exception as e:
            traceback.print_exc()
            self.logger.exception(e)
        finally:
            self.onEnd()
        


    def tick(self, i):

        if self.simulationMode == SimulationMode.SYNCHRONOUS:
            world_snapshot = self.world.tick() # synchronous mode
            # print(f'Simulator: world_snapshot: {world_snapshot}, i: {i}')
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            world_snapshot = self.world.wait_for_tick() # asynchronous mode 
        
        if i % 100 == 0:
            print(f"Simulator: world ticks {i}")
        for onTicker in self.onTickers:
            onTicker(world_snapshot)

