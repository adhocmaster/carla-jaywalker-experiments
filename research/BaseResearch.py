from abc import abstractmethod
import logging
from typing import Tuple
from agents.navigation.behavior_agent import BehaviorAgent
from agents.pedestrians.PedestrianAgent import PedestrianAgent
import carla
import os
from lib import ClientUser, LoggerFactory, MapManager, MapNames, SimulationVisualization, NotImplementedInterface, SimulationMode
from settings.SourceDestinationPair import SourceDestinationPair
# from lib.SimulationMode import SimulationMode

class BaseResearch(ClientUser):
    def __init__(
            self, 
            name, 
            client: carla.Client, 
            mapName, logLevel, 
            outputDir:str = "logs", 
            simulationMode = SimulationMode.ASYNCHRONOUS
        ) -> None:
        super().__init__(client)

        self.name = name
        self.mapName = mapName
        self.logLevel = logLevel
        self.outputDir = outputDir

        logPath = os.path.join(outputDir, f"{name}.log")
        self.logger = LoggerFactory.getBaseLogger(name, defaultLevel=logLevel, file=logPath)

        self.simulationMode = simulationMode

        self.time_delta = None
        self.mapManager = None
        self.visualizer = None
        self.mapManager: MapManager = None


        self.initWorldSettings()
        self.initVisualizer()

        pass


    def configureMap(self):
        self.mapManager = MapManager(self.client)
        self.mapManager.load(self.mapName, forceReload=True)

    def reset(self):
        # self.client.reload_world(False)
        self.mapManager.reload()


    def initWorldSettings(self):
        # settings = self.world.get_settings()
        # settings.substepping = False
        # settings.fixed_delta_seconds = self.time_delta
        # self.world.apply_settings(settings)
        
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.logger.warn(f"Starting simulation in asynchronous mode")
            self.initWorldSettingsAsynchronousMode()
        else:
            self.logger.warn(f"Starting simulation in synchronous mode")
            self.initWorldSettingsSynchronousMode()

        pass

    
    def initVisualizer(self):
        self.visualizer = SimulationVisualization(self.client, self.mapManager)
        self.visualizer.drawSpawnPoints(life_time=1.0)
        self.visualizer.drawSpectatorPoint()
        # self.visualizer.drawAllWaypoints(life_time=1.0)
        pass

    def initWorldSettingsAsynchronousMode(self):
        self.configureMap()
        self.time_delta = 0.007
        settings = self.world.get_settings()
        settings.synchronous_mode = False # Enables synchronous mode
        settings.substepping = False
        settings.fixed_delta_seconds = self.time_delta
        self.world.apply_settings(settings)
        pass

    def initWorldSettingsSynchronousMode(self):
        self.time_delta = 0.04
        settings = self.world.get_settings()
        # settings.substepping = False # https://carla.readthedocs.io/en/latest/python_api/#carlaworldsettings
        settings.synchronous_mode = True # Enables synchronous mode
        settings.fixed_delta_seconds = self.time_delta # Sets fixed time step
        self.world.apply_settings(settings)
        self.configureMap()
        pass

    def tickOrWaitBeforeSimulation(self):
        """
        It will not call simulation events. Only purpose is for some intializations which needs to be applied before simulation runs, e.g., actor creation.
        """
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.world.wait_for_tick()
        else:
            self.world.tick()

    @abstractmethod
    def createDynamicAgents(self):
        raise NotImplementedInterface("createDynamicAgents")

    @abstractmethod
    def setupSimulator(self):
        raise NotImplementedInterface("setupSimulator")
    

    # utility methods
    
    
    def createVehicle(self, vehicleSetting: SourceDestinationPair, maxSpeed: float, logLevel=logging.INFO) -> Tuple[carla.Vehicle, BehaviorAgent]:
        vehicleSpawnPoint = self.settingsManager.locationToVehicleSpawnPoint(vehicleSetting.source)
        
        vehicle = self.vehicleFactory.spawn(vehicleSpawnPoint)       
        if vehicle is None:
            self.logger.error("Cannot spawn vehicle")
            exit("Cannot spawn vehicle")
        else:
            self.logger.info(f"successfully spawn vehicle at {vehicleSpawnPoint.location.x, vehicleSpawnPoint.location.y, vehicleSpawnPoint.location.z}")

        self.tickOrWaitBeforeSimulation() # otherwise we can get wrong vehicle location!

        vehicleAgent = self.vehicleFactory.createSpeedControlledBehaviorAgent(vehicle, max_speed=maxSpeed, behavior='normal', logLevel=logLevel)

        spawnXYLocation = carla.Location(x=vehicleSpawnPoint.location.x, y=vehicleSpawnPoint.location.y, z=0.001)

        destination = vehicleSetting.destination
        vehicleAgent.set_destination(destination, start_location=spawnXYLocation)

        # raise Exception("stop")
        plan = vehicleAgent.get_local_planner().get_plan()
        # Utils.draw_trace_route(self._vehicle.get_world().debug, plan)
        self.visualizer.drawTraceRoute(plan, color=(10, 10, 0, 0), life_time=15.0)
        self.visualizer.drawDestinationPoint(destination, color=(0, 0, 255, 0), life_time=15.0)

        return vehicle, vehicleAgent
    
    def createWalker(self, walkerSetting: SourceDestinationPair) -> Tuple[carla.Walker, PedestrianAgent]:

        walkerSpawnPoint = carla.Transform(location = walkerSetting.source)
        
        self.visualizer.drawWalkerNavigationPoints([walkerSpawnPoint])


        walker = self.pedFactory.spawn(walkerSpawnPoint)

        if walker is None:
            self.logger.error("Cannot spawn walker")
            exit("Cannot spawn walker")
        else:
            self.logger.info(f"successfully spawn walker {walker.id} at {walkerSpawnPoint.location.x, walkerSpawnPoint.location.y, walkerSpawnPoint.location.z}")
            self.logger.info(walker.get_control())
            
            # visualizer.trackOnTick(walker.id, {"life_time": 1})      
        
        # self.world.wait_for_tick() # otherwise we can get wrong agent location!
        self.tickOrWaitBeforeSimulation()


        walkerAgent = self.pedFactory.createAgent(walker=walker, logLevel=self.logLevel, optionalFactors=[], config=None)

        walkerDestination = walkerSetting.destination
        walkerAgent.setDestination(walkerDestination)
        self.visualizer.drawDestinationPoint(walkerDestination, life_time=15.0)

        self.setWalkerDebugSettings(walkerAgent, walkerSetting)

        return walker, walkerAgent


    def setWalkerDebugSettings(self, walkerAgent: PedestrianAgent, walkerSetting: SourceDestinationPair):
        walkerSpawnPoint = carla.Transform(location = walkerSetting.source)

        walkerAgent.debug = False
        walkerAgent.updateLogLevel(logging.WARN)

        visualizationForceLocation = self.settingsManager.getVisualizationForceLocation()
        if visualizationForceLocation is None:
            visualizationForceLocation = walkerSpawnPoint.location
        
        visualizationInfoLocation = carla.Location(x=visualizationForceLocation.x + 2, y=visualizationForceLocation.y + 2, z=visualizationForceLocation.z)

        
        walkerAgent.visualizationForceLocation = visualizationForceLocation
        walkerAgent.visualizationInfoLocation = visualizationInfoLocation

    
    def updateWalker(self, world_snapshot, walkerAgent: PedestrianAgent, walker: carla.Walker):

        # print("updateWalker")
        if not walker.is_alive:
            return
        
        if walkerAgent is None:
            self.logger.warn(f"No walker to update")
            return

        if walkerAgent.isFinished():
            self.logger.warn(f"Walker {walkerAgent.walker.id} reached destination")
            walker.apply_control(walkerAgent.getStopControl())
            return
        
        control = walkerAgent.calculateControl()
        # print("apply_control")
        walker.apply_control(control)
            
    def updateVehicle(self, world_snapshot, vehicleAgent: BehaviorAgent, vehicle: carla.Vehicle):
        if not vehicle.is_alive:
            return

        if vehicleAgent is None:
            self.logger.warn(f"No vehicle to update")
            return 

        if vehicleAgent.done():
            self.logger.info(f"vehicle {vehicle.id} reached destination")
            vehicle.apply_control(carla.VehicleControl())
            return

        
        control = vehicleAgent.run_step()
        control.manual_gear_shift = False
        self.logger.info(control)
        vehicle.apply_control(control)
        pass

    
    
    def destoryActors(self):
        
        self.logger.info('\ndestroying  walkers')
        self.pedFactory.reset()
        self.logger.info('\ndestroying  vehicles')
        self.vehicleFactory.reset()