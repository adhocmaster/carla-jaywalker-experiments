import eventlet
import time
from .ClientUser import ClientUser
from .LoggerFactory import LoggerFactory
import traceback

class Simulator(ClientUser):

    def __init__(self, client, onTickers=None, onEnders=None, useThreads=False, sleep=0.05):
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

    def run(self, maxTicks):
        if self.useThreads:
            self.pool.spawn_n(self.loop, maxTicks)
        else:
            self.loop(maxTicks)

    
    def loop(self, maxTicks):

        try:
            for i in range(maxTicks):
                world_snapshot = self.world.wait_for_tick()
                if i % 100 == 0:
                    print(f"world ticks {i}")
                for onTicker in self.onTickers:
                    onTicker(world_snapshot)
                time.sleep(self.sleep)
                
        except Exception as e:
            traceback.print_exc()
            self.logger.exception(e)
        finally:
            self.onEnd()
        

    
    def onEnd(self):
        for onEnder in self.onEnders:
            onEnder()
