from xmlrpc.client import Boolean
from .Simulator import Simulator
import time


from .SimulationMode import SimulationMode

class EpisodeSimulator(Simulator):

    def __init__(self,
                    client, 
                    terminalSignalers=None, 
                    onTickers=None, 
                    onEnders=None, 
                    useThreads=False, 
                    sleep=0.05, 
                    simulationMode=SimulationMode.SYNCHRONOUS
                ):

        super().__init__(
            client=client,
            onTickers=onTickers,
            onEnders=onEnders,
            useThreads=useThreads,
            sleep=sleep,
            simulationMode=simulationMode
        )

        self.terminalSignalers = [] 
        if terminalSignalers is not None:
            self.terminalSignalers = terminalSignalers # this methods needs to be called to check for terminal states

    
    def isDone(self):
        for terminalSignaler in self.terminalSignalers:
            if terminalSignaler():
                return True
        return False
    

    
    def loop(self, maxTicks) -> Boolean:
        """Returns true if episode successfully ends

        Args:
            maxTicks (_type_): _description_

        Returns:
            bool: True if episode successfully ends, False otherwise.

        """

        try:
            for i in range(maxTicks):
                self.tick(i)
                if self.isDone():
                    # raise Exception("Episode finished")
                    self.logger.info("Episode finished")
                    return True
                
        except Exception as e:
            # traceback.print_exc()
            self.logger.exception(e)
        finally:
            self.onEnd()
        
        return False

    def tick(self, i):

        if self.simulationMode == SimulationMode.SYNCHRONOUS:
            world_snapshot = self.world.tick() # synchronous mode
            # print(f'Episodic Simulator: world_snapshot: {world_snapshot}, i: {i}')
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            world_snapshot = self.world.wait_for_tick() # asynchronous mode 
        
        if i % 100 == 0:
            print(f"Episodic Simulator: world ticks {i}")
        for onTicker in self.onTickers:
            onTicker(world_snapshot)

        time.sleep(self.sleep)
